from ipaddr import IPv4Network


class Cgn(IPv4Network):

    # @property
    def is_cgn(self):
        """Test if the address is RFC 6598 CGN reserved.

         Returns:
             A boolean, True if the address is within the
             reserved CGN IPv4 Network range.

        """
        return self in IPv4Network('100.64.0.0/10')
