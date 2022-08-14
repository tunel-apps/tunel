---
layout: app
name:  "{{ app.name }}"
launcher: "{{ app.launcher }}"
script: "{{ app.script }}"
maintainer: "@vsoch"
github: "{{ github_url }}"
script_url: "{{ script_url }}"
updated_at: "{{ creation_date }}"
description: "{{ app.description }}"
config: {{ app.config }}
---

### Usage

```bash
$ tunel run-app <server> {{ app.name }}
```

{% if app.config.args %}
#### Arguments

<div class="fresh-table">
<table class="table">
<thead>
  <th>Name</th>
  <th>Description</th>
  <th>Split By</th>
</thead>
<tbody>
{% for arg in app.config.args %}<tr>
   <td>{{ arg.name }}</td>
   <td>{{ arg.description }}</td>
   <td>{% if arg.split %}{{ arg.split }}{% else %}NA{% endif %}</td>
</tr>
{% endfor %}
</tbody></table></div>

<br>

If split by is provided, this means the argument takes a list, and you should use this as a delimiter.

{% endif %}

{% if app.config.needs %}
#### Needs
{% for need in app.config.needs %}
  - {{ need }}{% endfor %}
{% endif %}

{% if app.config.examples %}
### Examples

```bash
{{ app.config.examples }}```
{% endif %}

### Scripts

> {{ app.script }}

This app uses the {{ app.launcher }} launcher by default{% if app.launchers | length > 1 %}, and supports the following:

{% for launcher in app.launchers %}
  - {{ launcher }}{% endfor %}{% else %}.{% endif %}

```bash
{{ script }}
```

Have any questions, or want to request a new app or launcher? [Ask us!](https://github.com/tunel-apps/tunel/issues)

