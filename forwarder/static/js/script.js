var options = {
  valueNames: ['src_port', 'dst_ip', 'dst_port', 'comment']
};

var ruleList = new List('rules', options);
ruleList.sort('dst_ip', {order: 'asc'})
