from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from tv.models import Video, VideoCategory


@method_decorator(login_required, name='dispatch')
class TvView(TemplateView):
    """TV view for the app"""

    template_name = "tv.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context['featured_video'] = Video.objects.filter(is_featured=True).first()
        context['trending_videos'] = Video.objects.filter(is_trending=True)[:5]
        context['recommended_videos'] = Video.objects.order_by('-rating')[:5]
        context['sponsored_videos'] = Video.objects.filter(is_sponsored=True)[:4]
        context['recent_videos'] = Video.objects.order_by('-created_at')[:4]
        context['categories'] = VideoCategory.objects.all()
        return context


class CategoryVideosView(LoginRequiredMixin, ListView):
    """Videos filtered by category"""
    model = Video
    template_name = 'tv/category_videos.html'
    context_object_name = 'videos'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        return Video.objects.filter(category__slug=category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        context['category'] = VideoCategory.objects.get(slug=category_slug)
        return context


class VideoDetailView(LoginRequiredMixin, DetailView):
    """Detailed view for a single video"""
    model = Video
    template_name = 'tv/video_detail.html'
    context_object_name = 'video'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.get_object()
        context['related_videos'] = Video.objects.filter(
            category=video.category
        ).exclude(
            id=video.id
        )[:5]

        # Track view count
        video.view_count += 1
        video.save(update_fields=['view_count'])

        return context