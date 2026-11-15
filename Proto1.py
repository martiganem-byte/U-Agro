import streamlit as st
import time

from datetime import date, timedelta

from padron import find_rural_parcels, ParcelServiceError
from landsat_stac import obtener_bandas_landsat, LandsatError
from calculations import calculate_ndvi, calculate_ndmi
from nasa_power import obtener_datos_nasa_power, NASAPowerError
from responses import response_ndmi, response_ndvi

if "ndvi" not in st.session_state:
    st.session_state.ndvi = None

if "ndmi" not in st.session_state:
    st.session_state.ndmi = None

ndvi = st.session_state.ndvi
ndmi = st.session_state.ndmi


@st.cache_data(ttl=86400, show_spinner=False)
def consultar_clima(latitud, longitud):
    return obtener_datos_nasa_power(latitud, longitud)


st.image("Logo-UAgro.jpg")


tab1, tab2, tab3 = st.tabs(["About me!", "Get the info", "Let's talk"])

with tab1:
    st.title("Welcome to U-Agro!")
    col1, col2 = st.columns(2)
    with col1:
        st.header("**Who's behind this?**")
        st.text("Hi! My name is Mar and I'm a 17 year-old girl from Uruguay. In my country, agriculture represents huge part of the international income. However, this is a very unpredictable field, and that's why U-Agro was created...")
        st.divider()
        st.image(
            "foto-campo-uruguay.jpg")
        st.subheader("Why satellital data?")
        st.text("The main opponent of satellites are agro-drones, but there is one big difference: satellites provide simillar data by free, in constellations such as Sentinel or LandSat, which were used for this prototype.")

    with col2:
        st.divider()
        st.subheader("Fun fact #1:")
        st.text("Did you know that agriculture and its associated sub sectors represent approximately the 14% of Uruguay's GDP?")
        st.divider()
        st.header("About this project")
        st.text("U-Agro is a way to help local producers to evaluate their production condition throuhout satellital data.")
        st.divider()
        st.subheader("Fun fact #2:")
        st.text("Did you know that in 2022 and 2023 Uruguay lost 1811 million dollars just because of hydric stress and plagues?")


with tab2:
    st.subheader("Let's get started! :herb:")
    st.caption("Start by selecting you department and cadastral parcel number.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        dto = st.selectbox("Select department here.", options=["Artigas", "Canelones", "Cerro Largo", "Colonia", "Durazno", "Flores",
                                                               "Florida", "Lavalleja", "Maldonado", "Montevideo", "Paysandú", "Rivera",
                                                               "Río Negro", "Rocha", "Salto", "San José", "Soriano", "Tacuarembó", "Treinta y Tres"])

    with col2:
        padron = st.number_input("Parcel number:", 0, 999999)

    fecha_inicio, fecha_fin = st.date_input(
        "Landsat observation period:",
        value=(
            date.today() - timedelta(days=365),
            date.today()
        )
    )

    if st.button("Search parcel"):
        try:
            with st.spinner("Searching for your parcel..."):

                parcelas = find_rural_parcels(
                    dto,
                    int(padron)
                )

                if not parcelas:
                    st.warning("No parcel was found.")
                else:
                    parcela = parcelas[0]

                    st.success("Parcel found!")

                    resultado = obtener_bandas_landsat(
                        parcela["geometry"],
                        fecha_inicio.isoformat(),
                        fecha_fin.isoformat()
                    )

                    estadisticas = resultado["estadisticas"]

                    red = estadisticas["red"]["media"]
                    nir = estadisticas["nir"]["media"]
                    swir = estadisticas["swir"]["media"]

                    st.session_state.ndvi = calculate_ndvi(nir, red)
                    st.session_state.ndmi = calculate_ndmi(nir, swir)

                    st.divider()
                    st.subheader("Field Summary")

                    st.write("Department:", dto)
                    st.write("Parcel:", int(padron))
                    st.write("Satellite image date:", resultado["fecha"][:10])

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "NDVI",
                            "No data" if ndvi is None else f"{ndvi:.3f}"
                        )

                    with col2:
                        st.metric(
                            "NDMI",
                            "No data" if ndmi is None else f"{ndmi:.3f}"
                        )

                    st.caption(
                        "Indices calculated using mean band reflectance "
                        "values. Pixel-level calculations would be more "
                        "representative."
                    )

                    st.write(
                        "Scene cloud cover:",
                        resultado["nubosidad_escena"],
                        "%"
                    )

                    st.divider()
                    st.subheader("Historical Weather Analysis")

                    try:
                        with st.spinner("Analyzing historical weather data..."):

                            latitud = parcela["centroid"]["latitude"]
                            longitud = parcela["centroid"]["longitude"]

                            clima = consultar_clima(
                                latitud,
                                longitud
                            )

                        st.success("Weather data successfully retrieved!")

                        st.caption(
                            f"Historical period: "
                            f"{clima.index.min().date()} — "
                            f"{clima.index.max().date()}"
                        )

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Average temperature",
                                f"{clima['temperatura_media'].mean():.1f} °C"
                            )

                        with col2:
                            st.metric(
                                "Average daily rainfall",
                                f"{clima['precipitacion'].mean():.1f} mm"
                            )

                        with col3:
                            st.metric(
                                "Maximum temperature recorded",
                                f"{clima['temperatura_maxima'].max():.1f} °C"
                            )
                        with st.expander("View historical weather data"):

                            st.dataframe(
                                clima,
                                use_container_width=True
                            )

                    except NASAPowerError as error:
                        st.error(f"NASA POWER error: {error}")

        except ParcelServiceError as error:
            st.error(f"Parcel search error: {error}")

        except LandsatError as error:
            st.error(f"Landsat error: {error}")

    st.subheader("What parameters do we measure?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader(":green[NDVI]")
        st.text("The Normalized Difference Vegetation Index (NDVI) is a very commonly-used vegetation index which can tell how healthy our crop is by measuring how green it is.")

    with col2:
        st.subheader(":green[NDMI]")
        st.text("The Normalized Difference Moisture Index (NDMI) is used to determine vegetation water content. Are your plants thirsty?")

    with col3:
        st.subheader(":green[Weather trends]")
        st.text("Discover the average temperature and precipitations in the zone where your crop is. This is a very useful tool to use the weather to your favour!")


with tab3:
    st.title(":green[What do we do here?]")
    st.text("In this section we will analyze the information you recieved in 'Get the info', so you can understand everything crearly.")
    st.divider()

    question = None

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("This is Doña Marta!")
        st.text("She will help you if you don't understand something.")
        category = st.selectbox(
            "What would you want to know about?",
            ["I want to understand the indicators.",
                "Can you explain my statistics?"]
        )

        if category == "I want to understand the indicators.":
            questions = ["What is NDVI?", "What is NDMI?",
                         "What climate trends are measured?"]

        elif category == "Can you explain my statistics?":
            questions = ["What do my NDVI values mean?",
                         "What do my NDMI values mean?", "How can weather trends help me?"]

        if questions:
            question = st.selectbox("What would you like to know?", questions)

        if question == "What is NDVI?":
            st.write("""NDVI stands for Normalized Difference Vegetation Index. It helps us understand how green and dense your crops are by looking at how they reflect light.

            Let me explain how it works: healthy plants contain chlorophyll, a substance that absorbs red light for photosynthesis. Their leaves also reflect a lot of near-infrared light. When vegetation is sparse or stressed, it usually reflects more red light and less near-infrared light.

            That's the difference NDVI measures!""")
        elif question == "What is NDMI?":
            st.write("""NDMI stands for Normalized Difference Moisture Index. It helps estimate how much water is present in vegetation, especially in leaves and plant canopies.

            Here's how it works: satellites measure near-infrared and shortwave infrared light. Water in plants absorbs some of that shortwave infrared light. When vegetation loses water, it usually reflects more of it.

            That's why NDMI can help us identify changes in vegetation moisture and possible water stress.""")
        elif question == "What climate trends are measured?":
            st.write("""U-Agro uses temperature and rainfall data to help you understand local climate patterns.

            You can explore up to 30 years of historical data! You can check how much rain fell and what the maximum, minimum, and average temperatures were.

            This information can help you compare different seasons and understand how weather conditions have changed over time.""")
        elif question == "How can weather trends help me?":
            st.write("""Weather trends are very useful for comparing growing seasons and identifying patterns.

            This information on its own may not tell you much, but you can discuss it with an agricultural specialist to identify patterns and find ways to improve your crop management in future seasons.""")
        elif question == "What do my NDVI values mean?":
            st.write(response_ndvi(ndvi))
        elif question == "What do my NDMI values mean?":
            st.write(response_ndmi(ndmi))
        else:
            []

    with col2:
        st.image("doña_marta.jpg")
