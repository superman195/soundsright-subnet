import asyncio
import bittensor as bt 
import json

def timeout_decorator(timeout):
    """
    Uses asyncio to create an arbitrary timeout for an asynchronous
    function call. This function is used for ensuring a stuck function
    call does not block the execution indefinitely.

    Inputs:
        timeout:
            The amount of seconds to allow the function call to run
            before timing out the execution.

    Returns:
        decorator:
            A function instance which itself contains an asynchronous
            wrapper().

    Raises:
        TimeoutError:
            Function call has timed out.
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                # Schedule execution of the coroutine with a timeout
                return await asyncio.wait_for(func(*args, **kwargs), timeout)
            except asyncio.TimeoutError:
                # Raise a TimeoutError with a message indicating which function timed out
                raise TimeoutError(
                    f"Function '{func.__name__}' execution timed out after {timeout} seconds."
                )

        return wrapper

    return decorator

def validate_uid(uid):
    """
    This method makes sure that a uid is an int instance between 0 and
    255. It also makes sure that boolean inputs are filtered out as
    non-valid uid's.

    Arguments:
        uid:
            A unique user id that we are checking to make sure is valid.
            (integer between 0 and 255).

    Returns:
        True:
            uid is valid--it is an integer between 0 and 255, True and
            False excluded.
        False:
            uid is NOT valid.
    """
    # uid must be an integer instance between 0 and 255
    if not isinstance(uid, int) or isinstance(uid, bool):
        return False
    if uid < 0 or uid > 255:
        return False
    return True
    
def validate_miner_response(response):
    
    validation_dict = {
        'hf_model_namespace':str,
        'hf_model_name':str,
        'hf_model_revision':str,
    }

    if not isinstance(response,dict):
        return False
    
    if len(response.keys()) != 3: 
        return False

    for k in response.keys():
        if k not in validation_dict.keys() or not isinstance(response[k], validation_dict[k]) or response[k] == "":
            return False
        
    if response["hf_model_namespace"] == "synapsecai":
        return False
    
    return True
    
def validate_model_benchmark(model_benchmark):
    
    validation_dict = {
        'hf_model_namespace':str,
        'hf_model_name':str,
        'hf_model_revision':str,
        'hotkey':str,
        'model_hash':str,
        'block':int,
        'metrics':dict,
    }

    if not isinstance(model_benchmark, dict):
        return False
    
    for k in model_benchmark.keys():
        if k not in validation_dict.keys() or not isinstance(model_benchmark[k], validation_dict[k]):
            return False
        
    return True

def sign_data(hotkey: bt.Keypair, data: str) -> str:
    """Signs the given data with the wallet hotkey
    
    Arguments:
        wallet:
            The wallet used to sign the Data
        data:
            Data to be signed
    
    Returns:
        signature:
            Signature of the key signing for the data
    """
    try:
        signature = hotkey.sign(data.encode()).hex()
        return signature
    except TypeError as e:
        bt.logging.error(f'Unable to sign data: {data} with wallet hotkey: {hotkey.ss58_address} due to error: {e}')
        raise TypeError from e
    except AttributeError as e:
        bt.logging.error(f'Unable to sign data: {data} with wallet hotkey: {hotkey.ss58_address} due to error: {e}')
        raise AttributeError from e
    
def dict_in_list(target_dict, list_of_dicts) -> bool:
    """
    Returns True if the target_dict is within the list_of_dicts, regardless of the order of keys. Returns False otherwise.
    """
    target_str = json.dumps(target_dict, sort_keys=True)
    return any(json.dumps(d, sort_keys=True) == target_str for d in list_of_dicts)

def extract_metadata(list_of_dicts):
    needed_keys=["hf_model_namespace", "hf_model_name", "hf_model_revision"]
    output = []
    for d in list_of_dicts:
        # Only proceed if all needed keys are present
        if not all(k in d for k in needed_keys):
            continue

        output_dict = {k: d[k] for k in needed_keys}
        output.append(output_dict)
    return output