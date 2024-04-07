from supsisim.RCPblk import RCPblk
from numpy import size

def clarke_inverseBlk(pin, pout, output_type, offset):
    """

    Call:   clarke_inverseBlk(pin, pout)

    Parameters
    ----------
       pin: connected input port(s)
       pout: connected output port(s)

    Returns
    -------
        blk  : RCPblk

    """

    blk = RCPblk('inverse_clarke', pin, pout, [0,0], 1, [offset], [output_type])
    return blk

