"""Sahifa bo'sh ko'rinmasligi uchun namunaviy ma'lumot qo'shadi."""
import datetime as dt

from django.core.management.base import BaseCommand

from core.models import (
    Education, Experience, LanguageSkill, Profile, Skill, SkillGroup, SocialLink,
)
from portfolio.models import Folder, Project


class Command(BaseCommand):
    help = "Namunaviy profil, ko'nikma, papka va loyihalarni yaratadi."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true",
            help="Avval mavjud namunaviy yozuvlarni o'chiradi.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            for model in (Project, Folder, Experience, Education, Skill, SkillGroup,
                          LanguageSkill, SocialLink):
                model.objects.all().delete()

        profile = Profile.load()
        profile.full_name = profile.full_name or "Ismingiz Familiyangiz"
        profile.masthead = profile.masthead or "oldfox"
        profile.headline = profile.headline or "Backend dasturchi · Django"
        profile.tagline = profile.tagline or (
            "Oddiy interfeys ortidagi murakkab tizimlarni quraman."
        )
        profile.edition_note = profile.edition_note or "Toshkent"
        profile.location = profile.location or "Toshkent, O'zbekiston"
        profile.email = profile.email or "salom@example.com"
        profile.footer_note = profile.footer_note or "oldfox.uz"
        if not profile.about:
            profile.about = (
                "<p>Salom! Men veb-ilovalar quraman — g'oyadan tortib ishlab turgan "
                "mahsulotgacha. Ko'proq Django, PostgreSQL va toza interfeyslar bilan "
                "ishlayman.</p><p>Bu sahifa bir vaqtning o'zida rezyumem ham, "
                "ishlarim arxivi hamdir. Har bir loyiha o'z papkasida turadi.</p>"
            )
        profile.save()

        if not SocialLink.objects.exists():
            SocialLink.objects.bulk_create([
                SocialLink(label="GitHub", handle="@username",
                           url="https://github.com/", order=1),
                SocialLink(label="Telegram", handle="@username",
                           url="https://t.me/", order=2),
                SocialLink(label="LinkedIn", handle="ismingiz",
                           url="https://linkedin.com/", order=3),
            ])

        if not SkillGroup.objects.exists():
            groups = {
                "Backend": ["Python", "Django", "DRF", "PostgreSQL", "Celery"],
                "Frontend": ["HTML", "CSS", "JavaScript", "Alpine.js"],
                "Asboblar": ["Git", "Docker", "Linux", "Figma"],
            }
            for i, (name, items) in enumerate(groups.items()):
                group = SkillGroup.objects.create(name=name, order=i)
                Skill.objects.bulk_create(
                    Skill(group=group, name=s, order=j) for j, s in enumerate(items)
                )

        if not LanguageSkill.objects.exists():
            LanguageSkill.objects.bulk_create([
                LanguageSkill(name="O'zbek tili", level="Ona tili", order=1),
                LanguageSkill(name="Rus tili", level="B2", order=2),
                LanguageSkill(name="Ingliz tili", level="B1", order=3),
            ])

        if not Experience.objects.exists():
            Experience.objects.create(
                role="Backend dasturchi", company="Studio Nomi",
                location="Toshkent", start_date=dt.date(2023, 3, 1),
                is_current=True, order=1,
                description=(
                    "<ul><li>Django asosidagi ichki tizimni noldan qurdim.</li>"
                    "<li>API javob vaqtini ikki barobar tezlashtirdim.</li>"
                    "<li>Kichik jamoaga mentorlik qildim.</li></ul>"
                ),
            )
            Experience.objects.create(
                role="Junior dasturchi", company="Birinchi ish joyi",
                location="Toshkent", start_date=dt.date(2021, 6, 1),
                end_date=dt.date(2023, 2, 1), order=2,
                description="<p>Mijozlar uchun veb-saytlar va kichik xizmatlar.</p>",
            )

        if not Education.objects.exists():
            Education.objects.create(
                degree="Kompyuter injiniringi", institution="TATU",
                location="Toshkent", start_date=dt.date(2018, 9, 1),
                end_date=dt.date(2022, 6, 1), order=1,
            )

        if not Folder.objects.exists():
            folders = [
                ("Veb-ilovalar", "sand", "Django va API asosidagi mahsulotlar"),
                ("Interfeys ishlari", "blush", "Dizayn va frontend tajribalari"),
                ("Tajribalar", "sage", "Kichik tadqiqotlar va o'yinlar"),
            ]
            for i, (name, tone, desc) in enumerate(folders):
                Folder.objects.create(name=name, tone=tone, description=desc, order=i)

        if not Project.objects.exists():
            web = Folder.objects.first()
            Project.objects.create(
                folder=web, title="Buyurtmalar boshqaruv tizimi",
                summary="Kichik ishlab chiqarish uchun buyurtma va ombor hisobi.",
                role="Backend va arxitektura", client="Ichki mahsulot",
                tech="Django, PostgreSQL, Celery, Docker", year=2024,
                is_featured=True, order=1,
                body=(
                    "<h2>Muammo</h2><p>Buyurtmalar qog'ozda va Excelda yuritilar edi — "
                    "hisobotlar har oy qo'lda yig'ilardi.</p>"
                    "<h2>Yechim</h2><p>Bitta tizimga birlashtirilgan buyurtma, ombor va "
                    "hisobot moduli.</p>"
                    "<ul><li>Rolga qarab huquqlar</li><li>Avtomatik oylik hisobot</li>"
                    "<li>Telegram orqali bildirishnoma</li></ul>"
                    "<blockquote>Oylik hisobot tayyorlash 2 kundan 10 daqiqaga tushdi.</blockquote>"
                    "<h3>Natija</h3><p>Xatoliklar sezilarli kamaydi, omborda real vaqt "
                    "qoldig'i paydo bo'ldi.</p>"
                ),
            )
            Project.objects.create(
                folder=Folder.objects.all()[1] if Folder.objects.count() > 1 else web,
                title="Shaxsiy sayt va portfolio",
                summary="Klassik tipografikani zamonaviy veb bilan birlashtirish.",
                role="Dizayn va kod", tech="Django, CSS, Quill", year=2025,
                is_featured=True, order=2,
                body=(
                    "<p>Maqsad — qog'oz tipografikasining xotirjam tuyg'usini berish, lekin "
                    "eskirgan ko'rinishga tushib qolmaslik.</p>"
                    "<h2>Qarorlar</h2>"
                    "<ul><li>Qaymoqrang fon va nozik chiziqlar</li>"
                    "<li>Ustunli matn va bosh harf (drop cap)</li>"
                    "<li>Papka ko'rinishidagi portfolio</li></ul>"
                ),
            )

        self.stdout.write(self.style.SUCCESS("Namunaviy ma'lumotlar tayyor."))
