class AltitudeError(Exception):
    MIN_ALTITUDE = -1
    MAX_ALTITUDE = 30

    def __init__(self, altitude: float) -> None:
        message = "altitude `{}` out of bounds `[{}, {}]`".format(
            altitude, self.MIN_ALTITUDE, self.MAX_ALTITUDE
        )
        super(AltitudeError, self).__init__(message)

    @classmethod
    def isValid(ctx, altitude: float) -> bool:
        return ctx.MIN_ALTITUDE <= altitude and altitude <= ctx.MAX_ALTITUDE
    
class SpotNotFoundException(Exception):
    def __init__( self,
                  date_str: str,
                  azimuth: float,
                  altitude: float
                  ) -> None:
        message = "Spot not found in [date: {}, azimuth: {}, altitude: {}]".format(
            date_str, azimuth, altitude
        )