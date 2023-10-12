from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from PIL import Image as PILImage
from .models import Image, ExpiringLink
from .serializers import UserSerializer, AddSerializer, ListSerializer, ImageSerializer, ExpiringLinkSerializer
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.utils import timezone
from .permissions import HasLinkPlanPermission

class LoginView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.data)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('list')
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logoutView(request):
    logout(request)
    return Response({'message': 'Wylogowano pomyślnie'})


class AddView(generics.CreateAPIView):
    serializer_class = AddSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ListView(generics.ListAPIView):
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        print(user_id)
        queryset = Image.objects.filter(uploaded_by_id=user_id)
        print(queryset)
        return queryset


class DetailView(generics.RetrieveAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ThumbnailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, height, image_id):
        image = get_object_or_404(Image, pk=image_id)

        if height.lower() == "original":
            try:
                img = PILImage.open(image.file.path)
                response = HttpResponse(content_type='image/jpeg')
                img.save(response, img.format)
                return response
            except Exception as e:
                print(f"Error processing original image: {str(e)}")
                return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        image_width = image.width
        image_height = image.height
        thumbnail_height = height

        if not image_width or not image_height or not thumbnail_height:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        try:
            width_scale = int(image_height) / int(thumbnail_height)
            thumbnail_scaled_width = int(image_width) / width_scale
            img = PILImage.open(image.file.path)
            img.thumbnail((int(thumbnail_scaled_width), int(thumbnail_height)))

            img_format = img.format.lower()
            response = HttpResponse(content_type=f'image/{img_format}')
            img.save(response, img_format)
            return response
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExpiringLinkCreateView(generics.CreateAPIView):
    serializer_class = ExpiringLinkSerializer
    permission_classes = [IsAuthenticated, HasLinkPlanPermission]
    queryset = ExpiringLink.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        image_id = request.data.get('image')
        expiration_time = int(request.data.get('expiration_time'))

        try:
            image = Image.objects.get(id=image_id)
            unique_key = ExpiringLink.generate_unique_key()
            expiration_datetime = datetime.now() + timedelta(seconds=expiration_time)

            expiring_link = ExpiringLink(
                user=user,
                image=image,
                unique_key=unique_key,
                expiration_date=expiration_datetime,
                expiration_time=expiration_time
            )
            expiring_link.save()

            temporary_link = f"/view-image/{unique_key}/"
            return Response({'temporary_link': temporary_link}, status=status.HTTP_201_CREATED)

        except Image.DoesNotExist:
            return Response({'error': 'Image with the provided ID does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class ViewImageView(generics.RetrieveAPIView):
    permission_classes = []
    queryset = ExpiringLink.objects.all()

    def retrieve(self, request, unique_key, *args, **kwargs):
        expiring_link = get_object_or_404(ExpiringLink, unique_key=unique_key)

        if expiring_link.expiration_date < datetime.now().date():
            return Response({'error': 'The link has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        image_url = expiring_link.image.file.url
        image_link = f'<a href="{image_url}">Zobacz zdjecie</a>'

        response = HttpResponse(image_link, content_type='text/html')
        return response