import json
import os
import time

config = {
    'spool_root': None,
}


def spool_file_path(service_name, port, host=None):
    if port is None:
        base_name = service_name
    else:
        if host is not None and host != '127.0.0.1':
            base_name = "%s:%s:%s" % (service_name, host, port)
        else:
            base_name = "%s:%s" % (service_name, port)
    return os.path.join(config['spool_root'], base_name)


def parse_spool_file_path(path):
    base_name = os.path.basename(path)

    if ':' in base_name:
        parts = base_name.rsplit(':', 2)
        service_name = parts[0]
        if len(parts) < 3:
            host = None
            port = int(parts[1])
        else:
            host = parts[1]
            port = int(parts[2])
    else:
        service_name = base_name
        host = None
        port = None

    return service_name, host, port


def serialize_spool_file_contents(reason, expiration=None, creation=None):
    """Serialize the contents of the spool file (as JSON).

    :param reason: a string representing the reason why the downtime exists.
    :param expiration: The unix time when this downtime should be considered valid until, or None for no expiry.
    :param creation: The unix time when this downtime was created, or None if unknown.
    :returns: A JSON-formatted dictionary with keys reason, expiration, and creation, corresponding to the parameters.
    """
    return json.dumps({
        "reason": reason,
        "expiration": expiration,
        "creation": (time.time() if creation is None else creation),
    })


def deserialize_spool_file_contents(contents):
    """Deserialize the contents of the spool file, with a reasonable default if the file was created by an older version
    of hacheck.

    :returns: contents, JSON-deserialized, or a dictionary representing with reason->contents, expiration->None, and
              creation->None. See serialize_spool_file_contents for the keys to expect in the dictionary.
    """

    try:
        # TODO: Enforce that this dictionary contains the expected keys.
        return json.loads(contents)
    except ValueError:
        # in case we're looking at a file created by earlier versions of hacheck
        return {
            "reason": contents,
            "expiration": None,
            "creation": None,
        }


def configure(spool_root, needs_write=False):
    access_required = os.W_OK | os.R_OK if needs_write else os.R_OK
    if os.path.exists(spool_root):
        if not os.access(spool_root, access_required):
            raise ValueError("Insufficient access to %s" % spool_root)
    else:
        os.mkdir(spool_root, 0o750)
    config['spool_root'] = spool_root


def is_up(service_name, port=None, host=None):
    """Check whether a service is asserted to be up or down. Includes the logic
    for checking system-wide all state

    :returns: (bool of service status, dict of info as returned by deserialize_spool_file_contents)
    """
    all_up, all_info = status("all")
    if all_up:
        # Check with port=None first, because if service foo is down, then service foo on port 123 should be down too.
        service_up, service_info = status(service_name, port=None)
        if service_up:
            return status(service_name, port=port, host=host)
        else:
            return service_up, service_info
    else:
        return all_up, all_info


def status(service_name, port=None, host=None):
    """Check whether a service is asserted to be up or down, without checking
    the system-wide 'all' state.

    :returns: (bool of service status, dict of info as returned by deserialize_spool_file_contents)
    """
    happy_retval = (True, {'service': service_name, 'reason': '', 'expiration': None})
    path = spool_file_path(service_name, port, host)
    try:
        with open(path, 'r') as f:
            info_dict = deserialize_spool_file_contents(f.read())
            info_dict['service'] = service_name
            expiration = info_dict.get('expiration')
            if expiration is not None and expiration < time.time():
                os.remove(path)
                return happy_retval
            return False, info_dict
    except IOError:
        return happy_retval


def status_all_down():
    """List all down services

    :returns: Iterable of pairs of (service name, port, dict of info as returned by deserialize_spool_file_contents)
    """
    for filename in os.listdir(config['spool_root']):
        service_name, host, port = parse_spool_file_path(filename)
        up, info = status(service_name, port=port, host=host)
        if not up:
            yield service_name, host, port, info


def up(service_name, port=None, host=None):
    try:
        os.unlink(spool_file_path(service_name, port, host))
    except OSError:
        pass


def down(service_name, reason="", port=None, host=None, expiration=None, creation=None):
    currently_up, info = status(service_name, port=port, host=host)

    # If we already downed the service for the same reason, leave the creation time alone. This allows a user to
    # repeatedly down a service to refresh its expiration time, and we will keep track of how long it has been down
    # for.
    if creation is None and (not currently_up) and reason == info['reason']:
        creation = info.get('creation', creation)

    with open(spool_file_path(service_name, port, host), 'w') as f:
        f.write(serialize_spool_file_contents(reason, expiration=expiration, creation=creation))
