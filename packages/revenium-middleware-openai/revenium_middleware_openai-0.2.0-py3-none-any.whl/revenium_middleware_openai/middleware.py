import logging
import datetime
import wrapt

from revenium_middleware_core import client, run_async_in_thread, shutdown_event

@wrapt.patch_function_wrapper('openai', 'chat.completions.create')
def create_wrapper(wrapped, _, args, kwargs):
    """
    Wraps the openai.ChatCompletion.create method to log token usage.
    """
    logging.debug("OpenAI chat.completions.create wrapper called")
    usage_metadata = kwargs.pop("usage_metadata", {})

    request_time_dt = datetime.datetime.now(datetime.timezone.utc)
    request_time = request_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    logging.debug(f"Calling wrapped function with args: {args}, kwargs: {kwargs}")

    response = wrapped(*args, **kwargs)
    logging.debug(
        "OpenAI chat.completions.create response: %s",
        response)
    response_time_dt = datetime.datetime.now(datetime.timezone.utc)
    response_time = response_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    request_duration = (response_time_dt - request_time_dt).total_seconds() * 1000
    response_id = response.id

    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    cached_tokens = response.usage.prompt_tokens_details.cached_tokens

    logging.debug(
        "OpenAI client.ai.create_completion token usage - prompt: %d, completion: %d, total: %d",
        prompt_tokens, completion_tokens, total_tokens
    )

    openai_finish_reason = None
    if response.choices:
        openai_finish_reason = response.choices[0].finish_reason

    finish_reason_map = {
        "stop": "END",
        "function_call": "END_SEQUENCE",
        "timeout": "TIMEOUT",
        "length": "TOKEN_LIMIT",
        "content_filter": "ERROR"
    }
    stop_reason = finish_reason_map.get(openai_finish_reason, "END")  # type: ignore

    async def metering_call():
        try:
            if shutdown_event.is_set():
                logging.warning("Skipping metering call during shutdown")
                return
            logging.debug("Metering call to Revenium for completion %s", response_id)
            # The client.ai.create_completion method is not async, so don't use await
            result = client.ai.create_completion(
                cache_creation_token_count=cached_tokens,
                cache_read_token_count=0,
                input_token_cost=0.0,
                output_token_cost=0.0,
                total_cost=0.0,
                output_token_count=completion_tokens,
                cost_type="AI",
                model=response.model,
                input_token_count=prompt_tokens,
                provider="OPENAI",
                reasoning_token_count=0,
                request_time=request_time,
                response_time=response_time,
                completion_start_time=response_time,
                request_duration=int(request_duration),
                stop_reason=stop_reason,
                total_token_count=total_tokens,
                transaction_id=response_id,
                trace_id=usage_metadata.get("trace_id"),
                task_id=usage_metadata.get("task_id"),
                task_type=usage_metadata.get("task_type"),
                subscriber_identity=usage_metadata.get("subscriber_identity"),
                organization_id=usage_metadata.get("organization_id"),
                subscription_id=usage_metadata.get("subscription_id"),
                product_id=usage_metadata.get("product_id"),
                source_id=usage_metadata.get("source_id"),
                ai_provider_key_name=usage_metadata.get("ai_provider_key_name"),
                agent=usage_metadata.get("agent")
            )
            logging.debug("Metering call result: %s", result)
        except Exception as e:
            if not shutdown_event.is_set():
                logging.warning(f"Error in metering call: {str(e)}")
                # Log the full traceback for better debugging
                import traceback
                logging.warning(f"Traceback: {traceback.format_exc()}")

    thread = run_async_in_thread(metering_call())
    thread.join(timeout=5.0)
    return response
