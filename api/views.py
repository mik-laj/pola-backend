from pola import logic, logic_ai
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from product.models import Product
from pola.models import Query
from report.models import Report, Attachment
from ai_pics.models import AIPics, AIAttachment
from django.conf import settings
import json
import os
import uuid
import time
import base64
import hmac
import urllib
from hashlib import sha1
from ratelimit.decorators import ratelimit

# API v3

@csrf_exempt
@ratelimit(key='ip', rate='2/s', block=True)
def add_ai_pics(request):
    device_id = request.GET['device_id']

    data = json.loads(request.body)
    product_id = data.get('product_id')
    files_count = data['files_count']
    file_ext = data['file_ext']
    mime_type = data['mime_type']

    original_width = data['original_width']
    original_height = data['original_height']

    #TODO: add some down scaling if needed
    width = original_width
    height = original_height

    device_name = data['device_name']
    flash_used = data.get('flash_used', None)
    was_portrait = data.get('was_portrait', None)

    product = Product.objects.get(pk=product_id)

    ai_pics = AIPics.objects.create(product=product,
                                    client=device_id,
                                    original_width= original_width,
                                    original_height= original_height,
                                    width= width,
                                    height= height,
                                    device_name= device_name,
                                    flash_used= flash_used,
                                    was_portrait= was_portrait
                                    )

    signed_requests = []
    if files_count and file_ext and mime_type:
        if files_count > 24:
            return HttpResponseForbidden("files_count can be between 0 and 24")

        for i in range(0, files_count):
            signed_request = attach_pic_internal(ai_pics, i, file_ext, mime_type)
            signed_requests.append(signed_request)

    return JsonResponse({'width': width,
                         'height': height,
                         'signed_requests': signed_requests})


def attach_pic_internal(ai_pics, file_no, file_ext, mime_type):
    object_name = '%s/%s_%s_%s.%s' % (str(ai_pics.product.code),
                str(ai_pics.id), str(file_no), str(uuid.uuid1()), file_ext)

    signed_request = create_signed_request(mime_type, object_name, settings.AWS_STORAGE_BUCKET_AI_NAME)

    attachment = AIAttachment(report=report)
    attachment.attachment.name = object_name
    attachment.save()

    return signed_request

@ratelimit(key='ip', rate='2/s', block=True)
def get_by_code_v3(request):

    result = get_by_code_internal(request, ai_supported = True)

    return JsonResponse(result)

# API v2

def get_by_code_internal(request, ai_supported = False):
    code = request.GET['code']
    device_id = request.GET['device_id']

    result, stats, product = logic.get_result_from_code(code)

    if product is not None:
        Query.objects.create(client=device_id, product=product,
                             was_verified=stats['was_verified'],
                             was_590=stats['was_590'],
                             was_plScore=stats['was_plScore'])

    if product:
        product.increment_query_count()
        if product.company:
            product.company.increment_query_count()

    if product and ai_supported:
        result = logic_ai.add_ask_for_pics(result)

    return result

@ratelimit(key='ip', rate='2/s', block=True)
def get_by_code_v2(request):

    result = get_by_code_internal(request)

    return JsonResponse(result)

@csrf_exempt
@ratelimit(key='ip', rate='2/s', block=True)
def create_report_v2(request):
    device_id = request.GET['device_id']

    data = json.loads(request.body)
    description = data['description']
    product_id = data.get('product_id', None)
    files_count = data.get('files_count', None)
    file_ext = data.get('file_ext', None)
    mime_type = data.get('mime_type', None)

    product = None
    if product_id:
        product = Product.objects.get(pk=product_id)

    report = Report.objects.create(product=product, description=description,
                                   client=device_id)

    signed_requests = []
    if files_count and file_ext and mime_type:
        if files_count>10:
            return HttpResponseForbidden("files_count can be between 0 and 10")

        for _ in range(0, files_count):
            signed_request = attach_file_internal(report, file_ext, mime_type)
            signed_requests.append(signed_request)

    return JsonResponse({'id': report.id,
                         'signed_requests':signed_requests})


def attach_file_internal(report, file_ext, mime_type):
    object_name = '%s/%s.%s' % (str(report.id), str(uuid.uuid1()), file_ext)

    signed_request = create_signed_request(mime_type, object_name, settings.AWS_STORAGE_BUCKET_NAME)

    attachment = Attachment(report=report)
    attachment.attachment.name = object_name
    attachment.save()

    return signed_request


def create_signed_request(mime_type, object_name, bucket_name):
    expires = int(time.time() + 60 * 60 * 24)
    amz_headers = "x-amz-acl:public-read"

    string_to_sign = "PUT\n\n%s\n%d\n%s\n/%s/%s" % \
                     (mime_type, expires, amz_headers,
                      bucket_name, object_name)

    signature = base64.encodestring(
        hmac.new(settings.AWS_SECRET_ACCESS_KEY.encode(),
                 string_to_sign.encode('utf8'), sha1).digest())
    signature = urllib.quote_plus(signature.strip())
    url = 'https://%s.s3.amazonaws.com/%s' % (settings.AWS_STORAGE_BUCKET_NAME,
                                              object_name)
    signed_request = '%s?AWSAccessKeyId=%s&Expires=%s&Signature=%s' % \
                     (url, settings.AWS_ACCESS_KEY_ID, expires, signature),
    return signed_request

@csrf_exempt
@ratelimit(key='ip', rate='2/s', block=True)
def attach_file_v2(request):
    device_id = request.GET['device_id']
    report_id = request.GET['report_id']

    report = Report.objects.get(pk=report_id)

    if report.client != device_id:
        return HttpResponseForbidden("Device_id mismatch")

    data = json.loads(request.body)
    file_ext = data['file_ext']
    mime_type = data['mime_type']

    signed_request = attach_file_internal(report, file_ext, mime_type)

    return JsonResponse({'signed_request': signed_request})

#--- API v1 (old)

@ratelimit(key='ip', rate='2/s', block=True)
def get_by_code(request, code):
    device_id = request.GET['device_id']

    product = logic.get_by_code(code=code)

    result = logic.serialize_product(product)

    Query.objects.create(client=device_id, product=product,
                         was_verified=result['verified'],
                         was_590=code.startswith('590'),
                         was_plScore=result['plScore'] is not None)

    if product:
        product.increment_query_count()
        if product.company:
            product.company.increment_query_count()

    return JsonResponse(result)


@csrf_exempt
@ratelimit(key='ip', rate='2/s', block=True)
def create_report(request):
    device_id = request.GET['device_id']

    data = json.loads(request.body)
    description = data['description']
    product_id = data.get('product_id', None)

    product = None
    if product_id:
        product = Product.objects.get(pk=product_id)

    report = Report.objects.create(product=product, description=description,
                                   client=device_id)

    return JsonResponse({'id': report.id})


@csrf_exempt
@ratelimit(key='ip', rate='2/s', block=True)
def update_report(request):
    device_id = request.GET['device_id']
    report_id = request.GET['report_id']

    data = json.loads(request.body)
    description = data['description']

    report = Report.objects.get(pk=report_id)

    if report.client != device_id:
        return HttpResponseForbidden("Device_id mismatch")

    report.description = description
    report.save()

    return JsonResponse({'id': report.id})


@csrf_exempt
@ratelimit(key='ip', rate='5/s', block=True)
def attach_file(request):
    device_id = request.GET['device_id']
    report_id = request.GET['report_id']

    report = Report.objects.get(pk=report_id)

    if report.client != device_id:
        return HttpResponseForbidden("Device_id mismatch")

    attachment = Attachment(attachment=request.FILES['file'], report=report)
    file_name, file_extension = os.path.splitext(attachment.attachment.name)
    attachment.attachment.name = str(uuid.uuid1()) + file_extension
    attachment.save()

    return JsonResponse({'id': attachment.id})
