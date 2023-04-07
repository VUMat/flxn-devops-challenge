{{/* Define a function to generate the full name of the application */}}
{{- define "helloworld-app.fullname" -}}
{{- printf "%s-%s" .Release.Name "helloworld-app" -}}
{{- end }}

{{/* Define a function to generate the name of the application */}}
{{- define "helloworld-app.name" -}}
{{- "helloworld-app" -}}
{{- end }}


{{/* This function returns the namespace for the chart */}}
{{- define "helloworld-app.namespace" -}}
{{- printf "%s" .Values.namespace | default .Release.Namespace -}}
{{- end -}}