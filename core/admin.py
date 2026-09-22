from django.contrib import admin

from .models import (
    Award, Education, Experience, LanguageSkill, Message, Profile, Skill,
    SkillGroup, SocialLink,
)


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "headline", "email", "updated_at")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("role", "company", "start_date", "end_date", "is_current")
    list_filter = ("is_current",)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("degree", "institution", "start_date", "end_date")


@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    inlines = [SkillInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "contact", "subject", "created_at", "is_read")
    list_filter = ("is_read",)


admin.site.register([Award, LanguageSkill, SocialLink])
admin.site.site_header = "Portfolio boshqaruvi"
