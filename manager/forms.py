#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django import forms
from manager.models import *


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article

        fields = [
            "name","content","category","tag","create_user"
        ]