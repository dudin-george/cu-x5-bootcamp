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

{{/*
Image with support for local override of tag.
If .Values.image.tag is set, use it. Otherwise fallback to global.image.tag.
*/}}
{{- define "recruiter-web.image" -}}
{{- $tag := .Values.global.image.tag -}}
{{- if .Values.image -}}
{{- if .Values.image.tag -}}
{{- $tag = .Values.image.tag -}}
{{- end -}}
{{- end -}}
{{ .Values.global.image.registry }}/recruiter-web:{{ $tag }}
{{- end }}
