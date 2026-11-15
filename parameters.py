# NDVI
ndvi_prom = 0.85


def ndvi(ndvi):
    if 0.6 <= ndvi <= ndvi_prom:
        print("Your NDVI is in the ideal range! This often means that your crop is in its maximmum capacity.")
    elif 0.15 <= ndvi < 0.6:
        print("Your NDVI is a bit below the usual ideal range, but this doesn't have to mean anything wrong. Pay attention to your crop and check its condition with an agricultural engineer.")
    elif ndvi < 0.15:
        print("Your NDVI is very below the usual ideal range, it seems like there is almost no vegetation, but this doesn't have to mean anything wrong. Pay attention to your crop and check its condition with an agricultural engineer.")
    elif ndvi > ndvi_prom:
        print("Your NDVI is higher than the usual ideal range, but this doesn't have to mean anything wrong. Pay attention to your crop and check its condition with an agricultural engineer.")


# NDMI

ndmi_prom = 0.4  # +-.2


def ndmi(ndmi):
    if ndmi_prom-0.2 <= ndmi <= ndmi_prom+0.2:
        print("Your NDMI is in the ideal range! This often means that your crop is in its maximmum capacity.")
    elif -0.4 <= ndmi < ndmi_prom-0.2:
        print("Your NDMI is below the usual ideal range, but this doesn't have to mean anything wrong. Pay attention to your crop and check its condition with an agricultural engineer.")
    elif ndmi < -0.4:
        print("Your NDMI is below the usual ideal range, it seems like there is almost no vegetation, but this doesn't have to mean anything wrong. Pay attention to your crop and check its condition with an agricultural engineer.")
    elif ndmi > ndmi_prom+0.2:
        print("Your NDMI is higher than the usual ideal range, but this doesn't have to mean anything wrong. Pay attention to your crop and check its condition with an agricultural engineer.")
