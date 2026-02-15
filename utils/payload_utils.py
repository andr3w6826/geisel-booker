 
import utils.user_utils as user_utils
from datetime import datetime
import utils.datetime_utils as datetime_utils
import urllib.parse
import re
from playwright.sync_api import sync_playwright

from difflib import get_close_matches

def calculate_eid(building: str, room: str) -> int:
    EID_MAP = {
        # ── Geisel 1st Floor West ──────────────────────────────────
        "Geisel 1040: 1st Floor West": 102827,
        "Geisel 1041: 1st Floor West": 103886,
        "Geisel 1042: 1st Floor West": 103887,
        "Geisel 1045: 1st Floor West": 103888,

        # ── Geisel 2nd Floor East ──────────────────────────────────
        "Geisel 2070: 2nd Floor East": 103892,
        "Geisel 2071: 2nd Floor East": 103893,
        "Geisel 2072: 2nd Floor East": 103894,
        "Geisel 2096a: 2nd Floor East": 102823,
        "Geisel 2096b: 2nd Floor East": 103889,

        # ── Geisel Service Hubs ────────────────────────────────────
        "Geisel Service Hub 1": 142340,
        "Geisel Service Hub 3": 142341,
        "Geisel Service Hub 4": 142342,

        # ── Geisel 5th Floor ───────────────────────────────────────
        "Geisel 518: 5th Floor": 103054,
        "Geisel 519: 5th Floor": 103055,
        "Geisel 522: 5th Floor": 103057,

        # ── Geisel 6th Floor ───────────────────────────────────────
        "Geisel 618: 6th Floor": 103058,
        "Geisel 619: 6th Floor": 103059,
        "Geisel 620: 6th Floor": 103060,
        "Geisel 622: 6th Floor": 103061,
        "Geisel 623: 6th Floor": 103062,
        "Geisel 624: 6th Floor": 103063,
        "Geisel 625: 6th Floor": 103064,
        "Geisel 626: 6th Floor": 103065,
        "Geisel 627: 6th Floor": 103066,
        "Geisel 629: 6th Floor": 103067,
        "Geisel 630: 6th Floor": 103068,
        "Geisel 631: 6th Floor": 103069,

        # ── Geisel 7th Floor ───────────────────────────────────────
        "Geisel 718: 7th Floor": 103070,
        "Geisel 719: 7th Floor": 103073,
        "Geisel 720: 7th Floor": 103074,
        "Geisel 721: 7th Floor": 103071,
        "Geisel 722: 7th Floor": 103075,
        "Geisel 723: 7th Floor": 81635,
        "Geisel 724: 7th Floor": 81636,

        # ── WongAvery 1st Floor ────────────────────────────────────
        "WongAvery 105: 1st Floor": 102829,
        "WongAvery 106: 1st Floor": 103857,
        "WongAvery 107: 1st Floor": 103830,
        "WongAvery 108: 1st Floor": 103858,
        "WongAvery 109: 1st Floor": 103859,
        "WongAvery 110: 1st Floor": 103860,

        # ── WongAvery 1st Floor Special Rooms ─────────────────────
        "WongAvery 123: Presentation Practice Room": 103862,
        "WongAvery 131: 1st Floor": 103864,
        "WongAvery 134: 1st Floor": 103865,

        # ── WongAvery 2nd Floor ────────────────────────────────────
        "WongAvery 201: 2nd Floor": 153012,
        "WongAvery 203: 2nd Floor": 103868,
        "WongAvery 204: 2nd Floor": 103870,
        "WongAvery 205: 2nd Floor": 103872,
        "WongAvery 206: 2nd Floor": 103875,
        "WongAvery 207: 2nd Floor": 103876,
        "WongAvery 214: 2nd Floor": 103877,
        "WongAvery 223: 2nd Floor": 103878,
        "WongAvery 224: 2nd Floor": 103879,
        "WongAvery 225: 2nd Floor": 103880,
        "WongAvery 226: 2nd Floor": 103881,
        "WongAvery 227: 2nd Floor": 103882,
        "WongAvery 228: 2nd Floor": 103883,
        "WongAvery 229: 2nd Floor": 103884,
        "WongAvery 230: 2nd Floor": 103885,
    }

    # normalize building name via fuzzy match against known buildings
    KNOWN_BUILDINGS = ["Geisel", "WongAvery"]
    building_match = get_close_matches(building, KNOWN_BUILDINGS, n=1, cutoff=0.5)
    if not building_match:
        raise ValueError(f"Could not match building '{building}' to Geisel or WongAvery.")
    canonical_building = building_match[0]

    # find all keys belonging to that building, then match by room number
    candidate_keys = [k for k in EID_MAP if k.startswith(canonical_building) and str(room) in k]

    if len(candidate_keys) == 1:
        matched = candidate_keys[0]
        print(f"Matched '{building} {room}' → '{matched}'")
        return EID_MAP[matched]
    elif len(candidate_keys) == 0:
        raise ValueError(f"Room '{room}' not found in {canonical_building}.")
    else:
        raise ValueError(f"Ambiguous match for room '{room}' in {canonical_building}: {candidate_keys}")

def construct_grid_payload():

    profile = user_utils.user_profile()

    # normalize building and room to strings upfront so int/str in JSON both work
    building = str(profile["building"])
    room = str(profile["room"])

    # BUILD LID
    building_match = get_close_matches(building, ["Geisel", "WongAvery"], n=1, cutoff=0.5)
    if not building_match:
        raise ValueError(f"Could not match building '{building}' to Geisel or WongAvery.")
    canonical_building = building_match[0]
    lid = "11273" if canonical_building == "Geisel" else "11274"

    # BUILD GID
    if canonical_building == "WongAvery":
        gid = "35690"
    elif "Service Hub" in room:
        gid = "35687"
    elif re.fullmatch(r'\d+', room) and 500 <= int(room) <= 724:
        gid = "35689"  # Geisel Tower floors 5-7
    else:
        gid = "0"  # Geisel 1st/2nd floor, show all

    # BUILD EID
    eid = calculate_eid(canonical_building, room)

    start = datetime_utils.compute_target_date(profile["advance_days"])
    end = datetime_utils.compute_target_date(profile["advance_days"] + 1)

    seat = "0"
    seatId = "0"
    zone = "0"
    pageIndex = "0"
    pageSize = "18"

    POST_BODY = f"lid={lid}&gid={gid}&eid={eid}&seat={seat}&seatId={seatId}&zone={zone}&start={start}&end={end}&pageIndex={pageIndex}&pageSize={pageSize}"

    print(f'lid: {lid}, gid: {gid}, eid: {eid}, start: {start}, end: {end}')
    return POST_BODY, {
        'lid': lid, 'gid': gid, 'eid': eid,
        'seat': seat, 'seatId': seatId, 'zone': zone,
        'start': start, 'end': end,
        'pageIndex': pageIndex, 'pageSize': pageSize
    }


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


def extract_session_id_from_html(html: str) -> str:
    m = re.search(r'logout\?session=(\d+)', html)
    if not m:
        raise RuntimeError("Session ID not found in HTML")
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

def construct_remove_payload(booking_id, payload_dict):
    payload = {
        "removeId": booking_id,
        "lid": payload_dict["lid"],
        "gid": payload_dict["gid"],
        "start": payload_dict["start"],
        "end": payload_dict["end"],
        "bookings[0][id]": booking_id,
        "bookings[0][eid]": payload_dict["eid"],
        "bookings[0][seat_id]": "0",
        "bookings[0][gid]": payload_dict["gid"],
        "bookings[0][lid]": payload_dict["lid"],
        "bookings[0][start]": payload_dict["start_0"],  # "YYYY-MM-DD HH:MM"
        "bookings[0][end]": payload_dict["end_0"],
        "bookings[0][checksum]": payload_dict["checksum_0"],
    }
    return urllib.parse.urlencode(payload)