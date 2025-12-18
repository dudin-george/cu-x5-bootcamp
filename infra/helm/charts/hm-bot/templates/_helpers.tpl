{{- define "hm-bot.fullname" -}}
hm-bot
{{- end }}

{{- define "hm-bot.labels" -}}
app: hm-bot
app.kubernetes.io/name: hm-bot
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "hm-bot.selectorLabels" -}}
app: hm-bot
{{- end }}

{{- define "hm-bot.image" -}}
{{ .Values.global.image.registry }}/hm-bot:{{ .Values.global.image.tag }}
{{- end }}
