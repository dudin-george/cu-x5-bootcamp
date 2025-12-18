{{- define "worker.fullname" -}}
worker
{{- end }}

{{- define "worker.labels" -}}
app: worker
app.kubernetes.io/name: worker
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "worker.selectorLabels" -}}
app: worker
{{- end }}

{{- define "worker.image" -}}
{{ .Values.global.image.registry }}/worker:{{ .Values.global.image.tag }}
{{- end }}
