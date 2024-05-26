from drf_spectacular.utils import OpenApiExample

_graph_data_example = {
    "information": {
        "time_zone": "America/Sao_Paulo (UTC-03)",
        "date_format": "ISO-8601",
        "start_date": "2024-05-15T17:15:41.602645-03:00",
        "end_date": "2024-05-16T14:15:39.424825-03:00",
        "count": 3,
        "fields": ["active_generated", "active_consumption"],
    },
    "timestamp": [
        "2024-05-16T15:15:39.534610-03:00",
        "2024-05-16T15:00:39.534610-03:00",
        "2024-05-16T14:30:39.398148-03:00",
    ],
    "traces": [
        {
            "field": "active_generated",
            "avg_value": 1.88,
            "max_value": 7.72,
            "min_value": 0.0,
            "values": [
                7.72,
                4.32,
                0.14,
            ],
        },
        {
            "field": "active_consumption",
            "avg_value": 0.0,
            "max_value": 0.01,
            "min_value": 0.0,
            "values": [
                0.01,
                0.01,
                0.0,
            ],
        },
    ],
}

graph_data_example = OpenApiExample(
    name="Standard Example",
    value=_graph_data_example,
    response_only=True,
    request_only=False,
    description="Example of a response with graph data.",
)

# =============================================================================

_daily_profile_hourly = [
    {
        "time": "00:00:00",
        "active_generated": 0.0,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 0.01,
    },
    {
        "time": "04:00:00",
        "active_generated": 0.0,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 0.01,
    },
    {
        "time": "08:00:00",
        "active_generated": 0.05,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 0.16,
    },
    {
        "time": "12:00:00",
        "active_generated": 15.95,
        "active_consumption": 0.0,
        "reactive_inductive": 0.86,
        "reactive_capacitive": 0.66,
    },
    {
        "time": "16:00:00",
        "active_generated": 17.99,
        "active_consumption": 0.0,
        "reactive_inductive": 1.13,
        "reactive_capacitive": 0.49,
    },
    {
        "time": "20:00:00",
        "active_generated": 1.22,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 1.22,
    },
    {
        "time": "23:00:00",
        "active_generated": 0.0,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 0.02,
    },
]


daily_profile_hourly_example = OpenApiExample(
    name="Name deve ser alterado",
    value=_daily_profile_hourly,
    response_only=True,
    request_only=False,
    description="Example of a response with daily profile hourly data.",
)

# =============================================================================
_ufer_report_example = {
    "Organization": "UnB - Universidade de Brasilia",
    "period": {"start_date": "2024-04-26T21:03:18.241000Z", "end_date": "2024-05-16T19:31:23.378600Z"},
    "total_measurements": 102430,
    "info": "Results in (%) above the threshold 92%.",
    "results": [
        {
            "located": "UAC - Unidade Acadêmica",
            "ip_address": "164.41.20.230",
            "total_measurements": 12024,
            "transductor": 6,
            "pf_phase_a": 68.7,
            "pf_phase_b": 68.7,
            "pf_phase_c": 68.7,
        },
        {
            "located": "UAC - Unidade Acadêmica",
            "ip_address": "164.41.20.231",
            "total_measurements": 12975,
            "transductor": 7,
            "pf_phase_a": 70.12,
            "pf_phase_b": 70.12,
            "pf_phase_c": 70.12,
        },
        {
            "located": "UED - Unidade de Ensino e Docência",
            "ip_address": "164.41.20.233",
            "total_measurements": 18711,
            "transductor": 8,
            "pf_phase_a": 98.3,
            "pf_phase_b": 98.3,
            "pf_phase_c": 98.3,
        },
        {
            "located": "LDTEA - Laboratório de Desenvolvimento de Transportes e Energias Alternativas",
            "ip_address": "164.41.20.236",
            "total_measurements": 12328,
            "transductor": 1,
            "pf_phase_a": 77.43,
            "pf_phase_b": 77.43,
            "pf_phase_c": 77.43,
        },
        {
            "located": "LDTEA - Laboratório de Desenvolvimento de Transportes e Energias Alternativas",
            "ip_address": "164.41.20.239",
            "total_measurements": 12349,
            "transductor": 4,
            "pf_phase_a": 70.55,
            "pf_phase_b": 70.55,
            "pf_phase_c": 70.55,
        },
    ],
}

ufer_report_example = OpenApiExample(
    name="Standard Example",
    value=_ufer_report_example,
    response_only=True,
    request_only=False,
    description="Example of a response with Ufer report data.",
)
# =============================================================================
_energy_report_example = {
    "Organization": "UnB - Universidade de Brasilia",
    "Descendants": [
        "FGA - Faculdade do Gama",
        "UED - Unidade de Ensino e Docência",
        "UAC - Unidade Acadêmica",
        "LDTEA - Laboratório de Desenvolvimento de Transportes e Energias Alternativas",
        "MESP - Módulo de Serviços e Equipamentos Esportivos",
        "RU - Restaurante Universitário",
        "FCE - Faculdade de Ceilandia",
    ],
    "period": {"start": "2024-05-04T06:15:34.561323Z", "end": "2024-05-16T19:30:38.663618Z"},
    "transductors": [
        "164.41.20.230",
        "164.41.20.231",
        "164.41.20.233",
        "164.41.20.234",
        "164.41.20.236",
        "164.41.20.237",
        "164.41.20.238",
        "164.41.20.239",
        "164.41.20.241",
    ],
    "total_measurements": 9133,
    "results": {
        "active_consumption": 6038.05,
        "active_generated": 7324.46,
        "reactive_inductive": 1063.47,
        "reactive_capacitive": 1466.24,
    },
}

energy_report_example = OpenApiExample(
    name="Standard Example",
    value=_energy_report_example,
    response_only=True,
    request_only=False,
    description="Example of a response with energy report data.",
)
# =============================================================================
