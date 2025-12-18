{{/*
Common labels
*/}}
{{- define "app.labels" -}}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{/*
Ingress host from values
*/}}
{{- define "app.ingressHost" -}}
{{ .Values.ingress.host }}
{{- end }}
