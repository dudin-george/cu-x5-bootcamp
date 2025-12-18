{{- define "recruiter-web.fullname" -}}
recruiter-web
{{- end }}

{{- define "recruiter-web.labels" -}}
app: recruiter-web
app.kubernetes.io/name: recruiter-web
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "recruiter-web.selectorLabels" -}}
app: recruiter-web
{{- end }}

{{- define "recruiter-web.image" -}}
{{ .Values.global.image.registry }}/recruiter-web:{{ .Values.global.image.tag }}
{{- end }}
