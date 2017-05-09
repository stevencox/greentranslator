# broad_pgm_translator.DefaultApi

All URIs are relative to *https://translator.ncats.io/broad-pgm-translator*

Method | HTTP request | Description
------------- | ------------- | -------------
[**evaluate_model_post**](DefaultApi.md#evaluate_model_post) | **POST** /evaluateModel | 
[**model_id_group_id_group_signature_get**](DefaultApi.md#model_id_group_id_group_signature_get) | **GET** /{modelID}/{groupID}/groupSignature | 
[**model_id_model_signature_get**](DefaultApi.md#model_id_model_signature_get) | **GET** /{modelID}/modelSignature | 
[**model_list_get**](DefaultApi.md#model_list_get) | **GET** /modelList | 


# **evaluate_model_post**
> InlineResponse2003 evaluate_model_post(model)



evaluate model

### Example 
```python
from __future__ import print_statement
import time
import broad_pgm_translator
from broad_pgm_translator.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = broad_pgm_translator.DefaultApi()
model = broad_pgm_translator.Model() # Model |

try: 
    api_response = api_instance.evaluate_model_post(model)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->evaluate_model_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model** | [**Model**](Model.md)|  | 

### Return type

[**InlineResponse2003**](InlineResponse2003.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **model_id_group_id_group_signature_get**
> InlineResponse2001 model_id_group_id_group_signature_get(model_id, group_id)



Get model signature

### Example 
```python
from __future__ import print_statement
import time
import broad_pgm_translator
from broad_pgm_translator.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = broad_pgm_translator.DefaultApi()
model_id = 'model_id_example' # str | Model identifier
group_id = 'group_id_example' # str | Model identifier

try: 
    api_response = api_instance.model_id_group_id_group_signature_get(model_id, group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->model_id_group_id_group_signature_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**| Model identifier | 
 **group_id** | **str**| Model identifier | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **model_id_model_signature_get**
> InlineResponse200 model_id_model_signature_get(model_id)



Get model signature

### Example 
```python
from __future__ import print_statement
import time
import broad_pgm_translator
from broad_pgm_translator.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = broad_pgm_translator.DefaultApi()
model_id = 'model_id_example' # str | Model identifier

try: 
    api_response = api_instance.model_id_model_signature_get(model_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->model_id_model_signature_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**| Model identifier | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **model_list_get**
> InlineResponse2002 model_list_get()



List available models

### Example 
```python
from __future__ import print_statement
import time
import broad_pgm_translator
from broad_pgm_translator.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = broad_pgm_translator.DefaultApi()

try: 
    api_response = api_instance.model_list_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->model_list_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

