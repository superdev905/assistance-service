from datetime import datetime

months = ["enero",
          "febrero",
          "marzo",
          "abril",
          "mayo",
          "junio",
          "julio",
          "agosto",
          "septiembre",
          "octubre",
          "noviembre",
          "diciembre",
          ]

dayNames = ["Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo"]


def format_date_to_string(date: datetime):

    now = date
    month = months[now.month-1]
    dayName = dayNames[now.weekday()]

    string_date = dayName + " " + \
        str(now.day) + " de " + month + " del " + str(now.year) + \
        " a las " + \
        "%s:% s" % (now.hour, now.minute if now.minute >
                    9 else "0"+str(now.minute))

    return string_date
