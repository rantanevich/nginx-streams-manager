function sortColumns(elem_id, key, fields) {
  if (document.getElementById(elem_id)) {
    var options = {
      valueNames: fields
    };

    var elem = document.getElementById(elem_id);
    if (elem.querySelectorAll('table > .list > tr').length) {
      var fieldList = new List(elem_id, options);
      fieldList.sort(key, {order: 'asc'});
    }
  }
}

sortColumns('onlink-routes', 'dst', ['dst', 'gateway', 'ifname']);
sortColumns('static-routes', 'dst', ['dst', 'gateway', 'ifname']);
sortColumns('addresses', 'ip', ['ip', 'prefix', 'ifname']);
sortColumns('streams', 'dst_ip', ['src_port', 'dst_ip', 'dst_port', 'comment']);
