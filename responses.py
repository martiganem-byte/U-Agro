def response_ndvi(ndvi):
    if ndvi is None:
        return "NDVI value is not available. Please check the input data."
    elif ndvi < 0:
        return ("""In many cases, a negative NDVI indicates areas without vegetation, especially bodies of water such as lakes or streams. Other surfaces may also produce low values.

        Remember that a negative value does not automatically tell us what's happening in your field. When in doubt, I always recommend consulting an agricultural specialist.""")
    elif 0 <= ndvi < 0.2:
        return ("""This range often indicates mostly bare soil or very sparse vegetation. It may also appear when plants are very young or under stress.

        However, NDVI values can vary considerably depending on the type of crop and its stage of development. If you're unsure about what your result means, I recommend discussing it with an agricultural specialist.""")
    elif 0.2 <= ndvi < 0.5:
        return ("""This range can mean several different things. Let me explain a few possibilities so you can consider which one might apply to your field:

        Your crops may be in an early stage of development, reaching maturity, or growing in an area with limited vegetation cover. It could also indicate vegetation under stress, perhaps due to a lack of water or nutrients.

        If you're not sure which situation applies to your field, I recommend consulting an agricultural specialist.""")
    elif 0.5 <= ndvi <= 1:
        return ("""This range often indicates dense, green vegetation. Higher values generally suggest more abundant green vegetation.

        Keep in mind that a high NDVI value does not guarantee that your crops are completely healthy. It is always important to consider the type of crop and its stage of development.""")


def response_ndmi(ndmi):
    if -1 <= ndmi < -0.4:
        return ("""These low values may indicate very little water in vegetation, or areas with little or no vegetation, such as exposed soil, rocks, or urban areas.

        If you're unsure about what your result means, I recommend consulting an agricultural specialist.""")
    elif -0.4 <= ndmi < 0:
        return ("""Values in this range may indicate low moisture content in vegetation and could suggest possible water stress.

        However, this does not necessarily mean that your crops are dry. Results can vary depending on the crop and its growing stage, so it's best to discuss them with an agricultural specialist.""")
    elif 0 <= ndmi < 0.4:
        return ("""These values may indicate a greater amount of moisture in vegetation than lower or negative values.

        However, there is no single ideal range for every crop. It's important to consider the type of vegetation and the time of year when interpreting your results.""")
    elif 0.4 <= ndmi <= 1:
        return ("""Higher values usually indicate greater moisture content in vegetation.

    This does not automatically mean that your plants have too much water. Different crops and growing conditions can produce different results, so I recommend consulting an agricultural specialist before drawing conclusions.""")
