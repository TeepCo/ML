import pandas as pd
import datetime

class Event:
    def __init__(self, t, type, loc_type, location):
        self.t = t
        self.type = type
        self.loc_type = loc_type
        self.location = location

    def serialize(self):
        ft = datetime.datetime.fromtimestamp(self.t).strftime("%d.%m %H:%M:%S")
        return self.t, ft,  self.type, self.loc_type, self.location

suffix = "_01"
routes = pd.read_csv(f"data/localized_routes{suffix}.csv")
operace = pd.read_csv("data/operaceDEV01_corr.csv")

events = []

for i in range(len(routes)):
    row = routes.iloc[i]
    events.append(Event(row["beat"], "nakládka", row["start_type"], row["start"]))
    events.append(Event(row["end_beat"], "vykládka", row["end_type"], row["end"]))

for i in range(len(operace)):
    row = operace.iloc[i]
    events.append(Event(int(row["cas_real"] / 1000.0 + 0.5), "operace",
                        f"{row['lokace_pred_typ']}/{row['lokace_po_typ']}",
                        f"{row['lokace_pred']}/{row['lokace_po']}")
                  )

efd = pd.DataFrame([e.serialize() for e in events],
                   columns=["time", "ftime", "type", "location_type", "location"])
efd.sort_values(by="time", inplace=True)

print(efd)
efd.to_csv("data/events_01.csv")
