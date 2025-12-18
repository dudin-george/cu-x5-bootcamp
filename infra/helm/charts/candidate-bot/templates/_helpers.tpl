{{- define "candidate-bot.fullname" -}}
candidate-bot
{{- end }}

{{- define "candidate-bot.labels" -}}
app: candidate-bot
app.kubernetes.io/name: candidate-bot
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "candidate-bot.selectorLabels" -}}
app: candidate-bot
{{- end }}

{{- define "candidate-bot.image" -}}
{{ .Values.global.image.registry }}/candidate-bot:{{ .Values.global.image.tag }}
{{- end }}
