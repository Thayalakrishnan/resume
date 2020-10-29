from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
# thirdparty imports
from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer


from .models import Post
from .serializers import PostSerializer


class PostView(mixins.ListModelMixin,mixins.CreateModelMixin,generics.GenericAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    
    def get(self, request, *args, **kwargs):
        return self.list(self,request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class PostCreateView(mixins.ListModelMixin, generics.CreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    
    def get(self, request, *args, **kwargs):
        return self.list(self,request, *args, **kwargs)


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class PostDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'post_detail.html'
    
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        #serializer = PostSerializer(post)
        data ={
            'post':post,
        }
        return Response(data)


class PostListView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'post_list.html'
    
    def get(self, request):
        queryset = Post.objects.all()
        data ={
            'queryset':queryset,
        }
        return Response(data)