{{- define "candidate-landing.fullname" -}}
candidate-landing
{{- end }}

{{- define "candidate-landing.labels" -}}
app: candidate-landing
app.kubernetes.io/name: candidate-landing
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "candidate-landing.selectorLabels" -}}
app: candidate-landing
{{- end }}

{{/*
Image with support for local override of tag.
If .Values.image.tag is set, use it. Otherwise fallback to global.image.tag.
*/}}
{{- define "candidate-landing.image" -}}
{{- $tag := .Values.global.image.tag -}}
{{- if .Values.image -}}
{{- if .Values.image.tag -}}
{{- $tag = .Values.image.tag -}}
{{- end -}}
{{- end -}}
{{ .Values.global.image.registry }}/candidate-landing:{{ $tag }}
{{- end }}

