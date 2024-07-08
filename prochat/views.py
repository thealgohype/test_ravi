from .models import *
from .serializers import *
from .services import *
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from chaty.llm import LLMChain
from rest_framework.response import Response
from datetime import datetime
from google.cloud import texttospeech
import google.auth
from google.oauth2 import service_account
import os
from django.contrib.auth.decorators import login_required
from bson import ObjectId
import pytz
import base64
from .models import mytest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

User = get_user_model()

class GoogleLoginApi(APIView):
    def get(self, request, *args, **kwargs):
        auth_serializer = AuthSerializer(data=request.GET)
        auth_serializer.is_valid(raise_exception=True)
        
        validated_data = auth_serializer.validated_data
        user_data, jwt_token = createJwtToken(validated_data)
        
        response = redirect(settings.BASE_APP_URL)
        response.set_cookie('dsandeavour_access_token', jwt_token, max_age = 60 * 24 * 60 * 60)
        return response
    
    def post(self, request, *args, **kwargs):
        pass

@csrf_exempt
@api_view(['GET'])
def get_user_all_records(request):
    if request.method == 'GET':
        users = User.objects.all()
        if users.exists():
            response_data = [
                {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                } for user in users
            ]
            return JsonResponse({'data': response_data}, safe=False, status=200)
        else:
            return JsonResponse({'message': 'No records found'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
@api_view(['POST', 'GET'])
def add_test(request):
    if request.method == 'POST':
        user = request.user
        if not user.is_authenticated:
            #return JsonResponse({'error': 'User not authenticated'}, status=401)
            user.email = 'default'
        
        data = request.data
        llm_text = data.get('LLM')
        text_data = data.get('text')

        res1 = LLMChain(llm_text, text_data)
        timestamp = datetime.now()

        # Save the data to your model
        session_id = timestamp.strftime("%Y-%m-%d")  # Using date as session identifier

        # Save the data to your model
        modeldb = mytest(
            val1=user.email,
            val2=timestamp,
            val3=llm_text,
            val4=text_data,
            val5=res1,
            session=session_id  
        )
        modeldb.save()

        # Prepare the response data
        data = {
            'Time_Initiated': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'LLM_type': llm_text,
            'input_text': text_data,
            'AI_text': res1,
            'User_Email': user.email
        }

        data1 = []
        for i in data:
            data1.append(data[i])
        data1 = [
            str(item) if isinstance(item, ObjectId) else item for item in data1
        ]
        #val = our_collection.find().sort('_id', -1).limit(1)
        #data = []
        #for row in val:
        #    row['_id'] = str(row['_id'])
        #    data.append(row)
        project_id = "upbeat-grammar-423310-i8"
        private_key = """-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCLYn+t1vJDDRqF\nEG8VRyTihN4At/sEAHf/q3IFRQ3D96E5jkLmQs5ELJmXpUm3R1rdi+XNPkhcEFwU\nh6lFkf4B2wLDkpyVeXZfeXYvo88C1ZAMhb33QWVQ3rkz6ijpM0d321POapVfvYE0\n5sSPYOjaiPHm8ulsdyDVMndwZ//kAAF/qcNpgTFXiWUFHLN11l0DXFzOir5PaX7N\n4utpSxqI+Q6MsRieJR0QNhYPXPXX2c2b3DuJoFDJzsQd3r1kNe6z5e6DacBjqPEX\nt3c1qoVdzHdXVFxRr4I8x0uwMJX8oZDfHoc0DeDaEx5DXRBBII1R6sIYv1yf5iuF\nfBXoQZDVAgMBAAECgf95JKLT9H2ayUjDXgUt+SeVuOU6uqzwTXf+PoRbEClmqVL3\nMy3x8x5TInBb3My0/s96vpx8RiWd3popPb9hOAIMms1MLaDqSScY0/hkb3r8e6E3\nQQZaX/wuzWUqOdpU1LzI71dnkDtDevFRiUBNXW0EgwG8OGOoYeGnarVkfP9qqU4B\npRA6hlQC1V8KPaCnBlnq+dnqtWf9CiNoplLvKtDwEJ7v3L3p0KSpAjWww9kJj2MD\nzSgL2sMQUc8mjoyBUnpb6fEa2owG1hVBTyDVeyAJfHyyJFMucvPNUeNkpcdsKmyf\n3XBIhUmQ48WvfMDG4aVJILZKzVfkNflKmIAN9+8CgYEAxNB6Z0ZSMCSDR1Y9mc/o\nfpPKLchsP3eFba1LhIOjJD2L3Bqs+EDcRKl5wxtpt6rP4Ky20NwTJRkZOwWEAP5p\nJtQreiAtqklWLlrUywqOvXBL+XoPhzzlSs5k2JWe2CXYIikKplmN99zQLqQVLmlQ\nYA6pBc4CLx6NuLyeQdfUeecCgYEAtUzevYFtpRz6K6KpaAJfxTB9Kfg+VuwWi7i1\nn8DZJewRFa3dYHqO9utzabwtTVxRWQAwJmUNrcw6klV9BfZYBKUsluIIIuWIIrRh\nXldHjKcwf/S0/PqWSY0i8yV1Ws9fLoVr0uBMoPrBrxqq5rdxWDdvwrZM15DQ1k5A\ncPFln+MCgYEAmjchMjsPu1lg5EzXB+a5LjVvfmBFMZXdnwri2XqsIoF3TYg5cGyi\nK8r/9blNJPVa3Zl3xkArYC5CbtTrkjvG+P3W82KzZXMBbGEPy+kB375WSa0y7azx\nnaQLsQnL5WIB8QJnreEONOF43pMDZdJvgFT8a+f4HiO6uL5S4xTTEJECgYBhS96h\nrusL2FA9yK7Hfbat2YbiVjIGbe7vjvIRyOoAWv8UNll+5GcDBnrKvM1HHgseC2bL\nxCGiKt8oFy7gW0MDQy15z9Xz/GCh11IF0is4xaTWlpnmxgiPcmnWOT0QvgdjrQCf\ni/Yz0j7NXS9oX/w5Do8w3KrCaRpaWGZm9nXGZwKBgQCNYSlAFejqLbblOZVQJbPX\ny2HmbAyPAcXK5uQzcj+19F/jgCBpIYto8dH0dmccw9vzdJT4EhU7Z2/iPLOLXEp5\nW5k42jMvWjaMOjJZtYSTHPSpLFCRHHu7EXRJglgvYRJoVTKH6qe5Y5rPMeTxdl9a\ntr0DnmPb+btQiqB1dAfzEA==\n-----END PRIVATE KEY-----\n"""
        client_email = "test-account@upbeat-grammar-423310-i8.iam.gserviceaccount.com"
        client_id = "116963889449646785199"
        client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/test-account%40upbeat-grammar-423310-i8.iam.gserviceaccount.com"

        key_content = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": os.getenv('private_key_id'),
            "private_key": private_key,
            "client_email": client_email,
            "client_id": client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url":
            "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": client_x509_cert_url
        }

        credentials = service_account.Credentials.from_service_account_info(
            key_content)

        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # Set the voice parameters
        #voice = texttospeech.VoiceSelectionParams(
        #    language_code="en-US",
        #    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Journey-O"
        )
        
        
        # Set the audio configuration
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            effects_profile_id=['small-bluetooth-speaker-class-device'],
            speaking_rate=1,
            pitch=1)

        synthesis_input = texttospeech.SynthesisInput(text=res1)
        response = client.synthesize_speech(input=synthesis_input,
                                            voice=voice,
                                            audio_config=audio_config)

        #return JsonResponse({'data1':data1},status=200)
        #return HttpResponse(response.audio_content, content_type='audio/mp3')
        #response_data = {'list': data1}
        #json_data = json.dumps(response_data)
        #response1 = HttpResponse(response.audio_content,
        #                        content_type='audio/mp3')
        #response1['Content-Disposition'] = 'attachment; filename="audio.mp3"'
        #response1['X-Custom-Header'] = json_data
        #return response1
        audio_content_base64 = base64.b64encode(
            response.audio_content).decode('utf-8')
        response_data = {'audio_content': audio_content_base64, 'data': data1}

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_grouped_data(request):
    if request.method == 'GET':
        user = request.user
        if not user.is_authenticated:
            #return JsonResponse({'error': 'User not authenticated'}, status=401)
            user.email = 'default'
        # Retrieve entries for the current user sorted by 'session'      
        entries = mytest.objects.filter(val1=user.email).order_by('session')

        # Organize data by 'session'
        grouped_data = {}
        for entry in entries:
            session_key = entry.session  # Adjust 'session' to the actual field name
            if session_key not in grouped_data:
                grouped_data[session_key] = []
            grouped_data[session_key].append({
                'val2': entry.val2,
                'val3': entry.val3,
                'val4': entry.val4,
                'val5': entry.val5
            })

        return JsonResponse({'grouped_data': grouped_data}, safe=False, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

