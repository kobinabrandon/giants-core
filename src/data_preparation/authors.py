from src.data_preparation.books import Book
from src.setup.paths import make_data_directories


class Author:
    def __init__(self, name: str, books: list[Book]) -> None:
        self.name: str = name
        self.books: list[Book] = books

    def download_books(self):
        for book in self.books:
            book.download()


def get_authors() -> list[Author]:

    nkrumah = Author(
        name="Kwame Nkrumah",
        books= [
            # Book(
            #     title="Neo-Colonialism, the Last Stage of imperialism",
            #     url="https://www.marxists.org/ebooks/nkrumah/nkrumah-neocolonialism.pdf",
            #     core_pages=range(4, 202)
            # ),
            #
            # Book(
            #     title="Dark Days in Ghana",
            #     url="https://www.marxists.org/subject/africa/nkrumah/1968/dark-days.pdf",
            #     core_pages=range(7, 163)
            # ), 
            #
            # Book(
            #     title="Africa Must Unite",
            #     url="https://www.marxists.org/subject/africa/nkrumah/1963/africa-must-unite.pdf",
            #     core_pages=range(5, 237)
            # ),
            #
            # Book(
            #     title="Class Struggle In Africa",
            #     url="https://ia601208.us.archive.org/22/items/class-struggle-in-africa/Class%20Struggle%20in%20Africa_text.pdf",
            #     core_pages=range(3, 69)
            # ),
            #
            # Book(
            #     title="Handbook of Revolutionary Warefare: A Guide to the Armed Phase of the African Revolution",
            #     url="http://www.itsuandi.org/itsui/downloads/Itsui_Materials/handbook-of-revolutionary-warfare-a-guide-to-the-armed-phase-of-the-african-revolution.pdf",
            #     core_pages=range(8, 71)
            # ),
            #
            # Book(
            #     title="Revolutionary Path", 
            #     url="https://www.sahistory.org.za/file/426894/download?token=t2k1HcFY",
            #     core_pages=range(7, 267)
            # ),
            #
            Book(
                title="Ghana's Policy at Home and Abroad", 
                url="https://www.marxists.org/subject/africa/nkrumah/1957/ghanas-policy.pdf",
                core_pages=range(2, 18)
            ),


        ] 
    )


    lumumba = Author(
        name="Patrice Émery Lumumba",
        books = [
            Book(
                title="",
                url="",
            )
        ]
    )


    sankara =  Author(
        name="Thomas Isidore Noël Sankara",
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

    marx = Author(
        name="Karl Marx",
        books=[
            Book(
                title="Capital Vol I",
                url="https://www.marxists.org/archive/marx/works/download/pdf/Capital-Volume-I.pdf",
                core_pages=None
            ),

            Book(
                title="Capital Vol II",
                url="https://www.marxists.org/archive/marx/works/download/pdf/Capital-Volume-II.pdf",
                core_pages=None
            ),

            Book(
                title="Capital Vol III",
                url="https://www.marxists.org/archive/marx/works/download/pdf/Capital-Volume-III.pdf",
                core_pages=None
            ),

            Book(
                title="Value, Price & Profit",
                url="https://www.marxists.org/archive/marx/works/download/pdf/value-price-profit.pdf",
                core_pages=None
            ),

            Book(
                title="Wage, Labour & Capital",
                url="https://www.marxists.org/archive/marx/works/download/pdf/wage-labour-capital.pdf",
                core_pages=None
            ),



        ]
    )


    garvey = Author(
        name="Marcus Garvey",
        books=[
            Book(
                title="The Philosophy & Opinions of Marcus Garvey",
                url="",
            ),

            Book(
                title="The Communist Manfesto",
                url="",
            ),


        ]
    )


    fanon = Author(
        name="Franz Fanon",
        books=[
            Book(
                title="Black Skin, White Masks",
                url="",
            ),

            Book(
                title="The Wretched of the Earth",
                url="",
            ),


        ]
    )


    vivekananda = Author(
        name="Swami Vivekananda",
        books=[
            Book(
                title="Raja Yoga",
                url="",
            ),

            Book(
                title="Lectures from Columbo to Almora",
                url="",
            ),

        ]
    )


    tutu =  Author(
        name="Desmond Tutu",
        books=[
            Book(
                title="No Future Without Forgiveness",
                url="",
            ),

        ]
    )


    malcom = Author(
        name="Malcom X",
        books=[
            Book(
                title="The Autobiography of Malcom X",
                url="",
            ),

        ]
    )


    merton =  Author(
        name="Thomas Merton",
        books=[
            Book(
                title="The Seven Storey Mountain",
                url="",
            ),

            Book(
                title="New Seeds of Comtemplation",
                url="",
            ),


        ]
    )


    day =  Author(
        name="Dorothy Day",
        books=[
            Book(
                title="The Long Loneliness",
                url="",
            ),

        ]
    )


    ghaffar_khan = Author(
        name="Abdul Ghaffar Khan",
        books=[
            Book(
                title="My Life and Struggle",
                url="",
            ),

        ]
    )


    king = Author(
        name="Martin Luther King",
        books=[
            Book(
                title="Stride Toward Freedom",
                url="",
            ),

            Book(
                title="Why We Can't Wait",
                url="",
            ),


        ]
    )
     
    rai = Author(
        name="Lala Lajpat Rai",
        books=[
            Book(
                title="The Story of My Deportation",
                url="",
            ),

            Book(
                title="Young India: An Interpretation and a History of the Nationalist Movement from Within",
                url="",
            ),

        ]
    )
     

    rizal = Author(
        name="José Rizal",
        books=[
            Book(
                title="Noli Me Tangere (Touch Me Not)",
                url="",
            ),

            Book(
                title="El Filibusterismo (The Reign of Greed)", 
                url="",
            ),


        ]
    )

    return [nkrumah, sankara, lumumba, vivekananda, malcom, king, rai, rizal, day, fanon, marx, merton, tutu, garvey] 


# if __name__ == "__main__":
#     make_data_directories()
#     nkrumah = get_authors()[0]
#     nkrumah.download_books()
