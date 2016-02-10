<!doctype html>
<html>
	<head>
		<meta charset="utf8" />
		<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet" />
		<link href="https://cdnjs.cloudflare.com/ajax/libs/jqPlot/1.0.8/jquery.jqplot.min.css" rel="stylesheet" />
		<script src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/jqPlot/1.0.8/jquery.jqplot.min.js"></script>
	</head>
	<body>
		<div class="container">
			<ul class="nav nav-tabs" role="tablist">
				<li role="presentation" class="active"><a href="#home" aria-controls="home" role="tab" data-toggle="tab">home</a></li>
{% for k,v in stats.items() %}
				<li role="presentation"><a href="#{{ k }}" aria-controls="{{ k }}" role="tab" data-toggle="tab">{{ k }}</a></li>
{% endfor %}
			</ul>
			<div class="tab-content">
				<div role="tabpanel" class="tab-pane active" id="home">
					Hello!
				</div>
{% for k,v in stats.items() %}
				<div role="tabpanel" class="tab-pane" id="{{ k }}">
					<div class="panel-group" id="accordion-{{ k }}" role="tablist">
	{% for name,data in v|dictsort %}
					<div class="panel panel-default">
						<div class="panel-heading" role="tab" id="heading-{{ k }}-{{ name }}">
							<h4 class="panel-title">
								<a role="button" data-toggle="collapse" data-parent="#accordion-{{ k }}" href="#collapse-{{ k }}-{{ name }}" aria-controls="collapse-{{ k }}-{{ name }}">
									{{ data.0 }}
								</a>
							</h4>
						</div>
						<div id="collapse-{{ k }}-{{ name }}" class="panel-collapse collapse" role="tabpanel" aria-labelledby="heading-{{ k }}-{{ name }}">
							<div class="panel-body">
		{% if data.1 == "listing" %}
								<table class="table table-striped table-condensed">
									<thead>
			{% for h in data.2 %}
										<th>{{ h }}</th>
			{% endfor %}
									</thead>
									<tbody>
			{% for row in data.3 %}
										<tr>
				{% for item in row %}
											<td>{{ item }}</td>
				{% endfor %}
										</tr>
			{% endfor %}
									</tbody>
								</table>
		{% elif data.1 == "table" %}
								<table class="table table-striped table-condensed">
									<thead>
										<th></th>
			{% for h in data.2 %}
										<th>{{ h }}</th>
			{% endfor %}
									</thead>
									<tbody>
			{% for row in data.4 %}
										<tr>
											<th>{{ data.3[loop.index0] }}</th>
				{% for item in row %}
											<td>{{ item }}</td>
				{% endfor %}
										</tr>
			{% endfor %}
									</tbody>
								</table>
		{% elif data.1 == "image" %}
								<img src="{{ data.2 }}" />
		{% endif %}
							</div>
						</div>
					</div>
	{% endfor %}
					</div> <!-- accordion -->
				</div>
{% endfor %}
			</div>
		</div>
	</body>
</html>
