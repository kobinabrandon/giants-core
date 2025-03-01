from src.data_preparation.sourcing import Book, Author


def wanted_books():

    castro = Author(
        name="Fidel Castro",
        books=[
            Book(
                title="History Will Absolve Me",
                url=""
            ),

            Book(
                title="Obama and the Empire",
                url=""
            ),

            Book(
                title="On Imperialist Globalization",
                url=""
            ),

            Book(
                title="Capitalism in Crisis: Globalization and World Politics Today",
                url=""
            ),

            Book(
                title="Guantánamo: Why the Illegal US Base Should Be Returned to Cuba",
                url=""
            ),

            Book(
                title="Selected Speeches of Fidel Castro",
                url=""
            ),

            Book(
                title="Cuba at the Crossroads",
                url=""
            ),

            Book(
                title="War, Racism and Economic Justice: The Global Ravages of Capitalism",
                url=""
            ),
        ],
    )

    sankara =  Author(
        name="Captain Thomas Isidore Noël Sankara",
        books = [
            Book(
                title="Thomas Sankara Speaks: The Burkina Faso Revolution",
                url="",
            ),

            Book(
                title="We are the Heirs of the World's Revolutions: Speeches from the Burkina Faso Revolution",
                url="",
            ),

            Book(
                title="Women's Liberation and the African Freedom Struggle",
                url="",
            )

        ]
    )

    return [castro, sankara]





