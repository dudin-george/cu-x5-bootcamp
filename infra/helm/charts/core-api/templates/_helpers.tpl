{{- define "core-api.fullname" -}}
core-api
{{- end }}

{{- define "core-api.labels" -}}
app: core-api
app.kubernetes.io/name: core-api
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "core-api.selectorLabels" -}}
app: core-api
{{- end }}

{{- define "core-api.image" -}}
{{ .Values.global.image.registry }}/core-api:{{ .Values.global.image.tag }}
{{- end }}
