 
import utils.user_utils as user_utils
from datetime import datetime
import utils.datetime_utils as datetime_utils
import urllib.parse
import re
from playwright.sync_api import sync_playwright


def construct_grid_payload():
    """
        Given a user preference dict and the grid JSON response, compute the checksum for the desired slot.
        user_pref: {
            "building": "Geisel",
            "room": "522",
            "hour1": "2:00pm",
            "advance_days": 1
        }
    """

    profile = user_utils.user_profile()

    # BUILD LID
    if profile["building"] == "Geisel":
        lid = "11273"  # Geisel: 11273
    else:
        lid = "11274" # WongAvery: 11274
    
    # BUILD GID
    if int(profile['room']) in range(500,725):
        gid = "35689" # Geisel Tower (F5-7): 35689
    elif profile['room'] in ["Service Hub Room 1", "Service Hub Room 2", "Service Hub Room 3", "Service Hub Room 4"]:
        gid = "35687" # Geisel Service Hubs: 35687
    elif lid == "11274":  # WongAvery
        gid = "35690" # WongAvery Study Rooms: 35690
    else:
        gid = "0" # Show all: 0
    
    # BUILD EID
    if profile['room'] == "522":
        eid = 103057 # Geisel 522: 103057
    else:
        eid = 103055 # Geisel 519: 103055

    start = datetime_utils.compute_target_date(profile["advance_days"])
    end = datetime_utils.compute_target_date(profile["advance_days"] + 1)

    #defaults
    seat = "0"
    seatId = "0"
    zone = "0"
    pageIndex = "0"
    pageSize = "18"

    # lid = "11273"  # Geisel: 11273, WongAvery: 11274
    # gid = "35689" # Geisel Tower (F5-7): 35689, Geisel Service Hubs: 35687 WongAvery Study Rooms: 35690, Show all: 0
    # eid = "103057" # Geisel 522: 103057 Geisel: 519: 103055
    # seat = "0"
    # seatId = "0"
    # zone = "0"
    # start = "2026-02-25" # interesting, looks like start and end have to be 1 day apart. 
    # end = "2026-02-26"
    # pageIndex = "0"
    # pageSize = "18"

    POST_BODY = f"lid={lid}&gid={gid}&eid={eid}&seat={seat}&seatId={seatId}&zone={zone}&start={start}&end={end}&pageIndex={pageIndex}&pageSize={pageSize}"

    print(f'lid: {lid}, gid: {gid}, eid: {eid}, start: {start}, end: {end}')
    return POST_BODY, {'lid': lid, 'gid': gid, 'eid': eid, 'seat': seat, 
                       'seatId': seatId, 'zone': zone, 
                       'start': start, 'end': end, 
                       'pageIndex': pageIndex, 'pageSize': pageSize}

def find_checksum(slots, start_str, eid):
    for s in slots:
        if s["start"] == start_str and s["itemId"] == eid:
            return s["checksum"]

    raise ValueError(
        f"No slot found for start={start_str}, itemId={eid}"
    )


def construct_add_payload(checksum, payload_dict, start_str):

    dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
    formatted_start = dt.strftime("%Y-%m-%d %H:%M")

    payload = {
        "add[eid]": payload_dict['eid'],
        "add[gid]": payload_dict['gid'],
        "add[lid]": payload_dict['lid'],
        "add[start]": formatted_start,
        "add[checksum]": checksum,
        "lid": payload_dict['lid'],
        "gid": payload_dict['gid'],
        "start": payload_dict['start'],
        "end": payload_dict['end'],
    }
    return urllib.parse.urlencode(payload), {
        'add[eid]': payload_dict['eid'],
        'add[gid]': payload_dict['gid'],
        'add[lid]': payload_dict['lid'],
        'add[start]': start_str[:-3],
        'add[checksum]': checksum,
        'lid': payload_dict['lid'],
        'gid': payload_dict['gid'],
        'start': payload_dict['start'],
        'end': payload_dict['end']
    }


def extract_add_response(add_response_json, grid_payload_dict):
    payload_dict = {}
    target_dict = add_response_json['bookings'][0]

    payload_dict['update_id'] = target_dict['id']
    payload_dict['update_checksum'] = target_dict['optionChecksums'][-1] # Get the last checksum in the list (longest time
    print(f"Longest duration checksum from add response: {payload_dict['update_checksum']}")
    payload_dict['update_end'] = target_dict['options'][-1] # lasttimeslot (ex. "2026-02-26 18:00:00")
    payload_dict['lid'] = target_dict['lid']
    payload_dict['gid'] = target_dict['gid']
    payload_dict['start'] = grid_payload_dict['start']
    payload_dict['end'] = grid_payload_dict['end']
    payload_dict['id_0'] = target_dict['id']
    payload_dict['eid'] = target_dict['eid']
    payload_dict['seat_id'] = target_dict['seat_id']
    payload_dict['gid_0'] = target_dict['gid']
    payload_dict['lid_0'] = target_dict['lid']
    payload_dict['start_0'] = target_dict['start']
    payload_dict['end_0'] = target_dict['end']
    payload_dict['checksum_0'] = target_dict['checksum'] # original checksum for the slot
    return payload_dict

def construct_update_payload(data: dict):
    start_0_fmt = datetime.strptime(
        data["start_0"], "%Y-%m-%d %H:%M:%S"
    ).strftime("%Y-%m-%d %H:%M")

    end_0_fmt = datetime.strptime(
        data["end_0"], "%Y-%m-%d %H:%M:%S"
    ).strftime("%Y-%m-%d %H:%M")
    payload = {
        # update block
        "update[id]": data["update_id"],
        "update[checksum]": data["update_checksum"],
        "update[end]": data["update_end"],  # keep full seconds

        # outer context
        "lid": data["lid"],
        "gid": data['gid'],  # IMPORTANT: outer gid = 0
        "start": data["start"],
        "end": data["end"],

        # bookings[0] block
        "bookings[0][id]": data["id_0"],
        "bookings[0][eid]": data["eid"],
        "bookings[0][seat_id]": data["seat_id"],
        "bookings[0][gid]": data["gid_0"],
        "bookings[0][lid]": data["lid_0"],
        "bookings[0][start]": start_0_fmt,
        "bookings[0][end]": end_0_fmt,
        "bookings[0][checksum]": data["checksum_0"], 
    }

    return urllib.parse.urlencode(payload)

def extract_update_response(update_json: dict) -> dict:

    b0 = update_json["bookings"][0]

    return {
        "booking_id": b0["id"],
        "eid": b0["eid"],
        "seat_id": b0['seat_id'],
        "gid": b0["gid"],
        "lid": b0["lid"],
        "start_dt": b0["start"],             # "YYYY-MM-DD HH:MM:SS"
        "end_dt": b0["end"],                 # "YYYY-MM-DD HH:MM:SS"
        "checksum": b0["checksum"],
    }

def construct_time_payload(d: dict) -> str:
    """
    d must contain:
      booking_id, eid, seat_id, gid, lid, start_dt, end_dt, checksum
    where start_dt/end_dt are "YYYY-MM-DD HH:MM:SS"
    """

    payload = {
        "patron": "",
        "patronHash": "",
        "returnUrl": "/reserve",
        "bookings[0][id]": d["booking_id"],
        "bookings[0][eid]": d["eid"],
        "bookings[0][seat_id]": d["seat_id"],
        "bookings[0][gid]": d["gid"],
        "bookings[0][lid]": d["lid"],
        "bookings[0][start]": datetime_utils.to_hhmm(d["start_dt"]),
        "bookings[0][end]": datetime_utils.to_hhmm(d["end_dt"]),
        "bookings[0][checksum]": d["checksum"],

        "method": 11,
    }
    return urllib.parse.urlencode(payload)


def extract_session_id(page) -> str:
    # Wait until the element exists in DOM (not necessarily visible)
    page.wait_for_selector("a#s-lc-eq-auth-lobtn", state="attached", timeout=30000)

    href = page.get_attribute("a#s-lc-eq-auth-lobtn", "href") or ""
    m = re.search(r"session=(\d{8})", href)
    if not m:
        raise RuntimeError(f"Session id not found in href: {href}")

    return m.group(1)

def construct_checkout_payload(session_id: int) -> dict:
    """
    Build checkout form-data payload.

    This must be sent as multipart/form-data.
    """
    return {
        "returnUrl": "/reserve",
        "logoutUrl": "logout",
        "session": str(session_id),
    }
