from loguru import logger
from src.data_preparation.sourcing import ViaHTTP, Author, ViaScraper


def prepare_sources():

   
    marx = Author(
        name="Karl Marx",
        books_via_http=[
            ViaHTTP(
                title="Capital Vol I",
                url="https://www.marxists.org/archive/marx/works/download/pdf/Capital-Volume-I.pdf",
                start_page=None,
                end_page=None
            ),

            ViaHTTP(
                title="Capital Vol II",
                url="https://www.marxists.org/archive/marx/works/download/pdf/Capital-Volume-II.pdf",
                start_page=None,
                end_page=None
            ),

            ViaHTTP(
                title="Capital Vol III",
                url="https://www.marxists.org/archive/marx/works/download/pdf/Capital-Volume-III.pdf",
                start_page=None,
                end_page=None
            ),

            ViaHTTP(
                title="Value, Price & Profit",
                url="https://www.marxists.org/archive/marx/works/download/pdf/value-price-profit.pdf",
                start_page=None,
                end_page=None
            ),

            ViaHTTP(
                title="Wage, Labour & Capital",
                url="https://www.marxists.org/archive/marx/works/download/pdf/wage-labour-capital.pdf",
                start_page=None,
                end_page=None
            ),

            ViaHTTP(
                title="The Communist Manifesto",
                url="https://www.marxists.org/admin/books/manifesto/Manifesto.pdf",
                start_page=30,
                end_page=112
            ),
        ]
    )


    mao = Author(
        name="Mao Zedong",
        books_via_http=[
            ViaHTTP(
                title="Oppose Book Worship",
                url="https://www.marxists.org/ebooks/mao/Oppose_Book_Worship_-_Mao_Zedong.pdf",
                start_page=2,
                end_page=12
            ),

            ViaHTTP(
                title="Selected Works of Mao Tse-Tung Volume I",
                url="https://www.marxists.org/reference/archive/mao/selected-works/sw-in-pdf/sw-flp-1965-v1.pdf",
                start_page=20,
                end_page=353
            ),

            ViaHTTP(
                title="Selected Works of Mao Tse-Tung Volume II",
                url="https://www.marxists.org/reference/archive/mao/selected-works/sw-in-pdf/sw-flp-1965-v2.pdf",
                start_page=18,
                end_page=473
            ),

            ViaHTTP(
                title="Selected Works of Mao Tse-Tung Volume III",
                url="https://www.marxists.org/reference/archive/mao/selected-works/sw-in-pdf/sw-flp-1965-v3.pdf",
                start_page=16,
                end_page=345
            ),

            ViaHTTP(
                title="Selected Works of Mao Tse-Tung Volume IV",
                url="https://www.marxists.org/reference/archive/mao/selected-works/sw-in-pdf/sw-flp-1965-v4.pdf",
                start_page=17,
                end_page=463
            ),

            ViaHTTP(
                title="Selected Works of Mao Tse-Tung Volume V",
                url="https://www.marxists.org/reference/archive/mao/selected-works/sw-in-pdf/sw-flp-1971-v5.pdf",
                start_page=22,
                end_page=524
            )
        ],
        books_via_scraper=[
            ViaScraper(
                title="Combat Liberalism",
                url="https://www.marxists.org/reference/archive/mao/selected-works/volume-2/mswv2_03.htm",
                initial_marker="We stand for",
                terminal_marker="Transcription"
            )
        ]
    )


    garvey = Author(
        name="Marcus Garvey",
        books_via_http=[
            ViaHTTP(
                title="The Philosophy & Opinions of Marcus Garvey",
                url="https://jpanafrican.org/ebooks/eViaHTTP%20Phil%20and%20Opinions.pdf",
                start_page=1,
                end_page=63
            ),
        ]
    )


    vivekananda = Author(
        name="Swami Vivekananda",
        books_via_http=[
            ViaHTTP(
                title="The Complete Works of Swami Vivekananda",
                url="https://ia801608.us.archive.org/9/items/complete-works-of-swami-vivekananda-all-volumes-swami-vivekananda/Complete%20Works%20of%20Swami%20Vivekananda%20-%20%20All%20Volumes%20-%20Swami%20Vivekananda.pdf",
                start_page=81,
                end_page=5162
            )
        ]
    )


    blavatsky = Author(
        name="Helena Pretrovna Blavatsky",
        books_via_http=[
            ViaHTTP(
                title="The Secret Doctrine (Volume I)",
                url="https://www.gutenberg.org/files/54824/54824-pdf.pdf",
                start_page=12,
                end_page=971
            ),
            
            ViaHTTP(
                title="The Secret Doctrine (Volume II)",
                url="https://www.gutenberg.org/files/54488/54488-pdf.pdf",
                start_page=23,
                end_page=1156
            ),

            ViaHTTP(
                title="The Secret Doctrine (Volume III)",
                url="https://www.gutenberg.org/files/56880/56880-pdf.pdf",
                start_page=9,
                end_page=796
            ),
        ],

        books_via_scraper=[
            ViaScraper(
                title="The Secret Doctrine (Volume IV)",
                url="https://www.gutenberg.org/ebooks/61626.epub.noimages",
            )
        ]
    
    )


    gandhi = Author(
        name="Mohandas Karamchand Ghandi",
        books_via_http=[
            ViaHTTP(
                title="An Autobiography: The Story of My Experiments with Truth",
                url="https://www.mkgandhi.org/ebks/An-Autobiography.pdf",
                start_page=16,
                end_page=556
            ),

            ViaHTTP(
                title="Hind Swaraj or Indian Home Rule",
                url="https://www.mkgandhi.org/ebks/hind_swaraj.pdf",
                start_page=12,
                end_page=89
            ),

            ViaHTTP(
                title="The Bhagavad Gita, According to Gandhi",
                url="https://ia800904.us.archive.org/10/items/InnerEngineeringAYogisGuideToJoy_20190116/Mahatma_gandhiThe_bhagavad_gita_according_to_gandhi.pdf",
                start_page=10,
                end_page=177
            ),

            ViaHTTP(
                title="Non-Violent Resistance",
                url="https://archive.org/details/nonviolentresist00mkga/page/n9/mode/2up",
                start_page=16,
                end_page=388
            )
        ]
    )


    rai = Author(
        name="Lala Lajpat Rai",
        books_via_http=[
            ViaHTTP(
                title="The Story of My Deportation",
                url="https://ia601503.us.archive.org/21/items/in.ernet.dli.2015.19903/2015.19903.The--Story-Of-My-Deportation_text.pdf",
                start_page=8,
                end_page=274,
                needs_ocr=True
            ),

            ViaHTTP(
                title="Young India: An Interpretation and a History of the Nationalist Movement from Within",
                url="https://ia800802.us.archive.org/21/items/16RaiYoungindia/16-rai-youngindia.pdf",
                start_page=7,
                end_page=294
            ),

        ]
    )


    rizal = Author(
        name="José Rizal",
        books_via_http=[
            ViaHTTP(
                title="The Social Cancer", 
                url="https://www.geocities.ws/qcpujoserizal/Rizal/pdf/Noli.pdf",
            ),
        ],

        books_via_scraper=[
            ViaScraper(
                title="The Reign of Greed", 
                url="https://www.gutenberg.org/files/10676/10676-h/10676-h.htm",
                initial_marker="On the Upper Deck",
                terminal_marker="Colophon"
            )
        ]
    )


    lenin = Author(
        name="Vladimir Lenin",
        books_via_http=[
            ViaHTTP(
                title="What Is to Be Done?: Burning Questions of our Movements",
                url="https://www.marxists.org/ebooks/lenin/what-is-to-be-done.pdf",
                start_page=7,
                end_page=124
            ),

            ViaHTTP(
                title="The State and Revolution",
                url="https://www.marxists.org/ebooks/lenin/state-and-revolution.pdf",
                start_page=7,
                end_page=83
            ),

        ]
    )


    yat_sen = Author(
        name="Sun Yat-sen",
        books_via_http=[
            ViaHTTP(
                title="The Three Principles of the People",
                url="https://chinese.larouchepub.com/wp-content/uploads/2017/05/San-Min-Chu-I_ALL-en.pdf",
                start_page=3,
                end_page=74
            ),

            ViaHTTP(
                title="The International Development of China",
                url="https://chinese.larouchepub.com/wp-content/uploads/2017/05/sun_IDC-en.pdf",
                start_page=15, 
                end_page=305
            ),
        ]
    )


    goldman = Author(
        name="Emma Goldman",
        books_via_http=[
            ViaHTTP(
                title="Anarchism and Other Essays",
                url="https://www.gutenberg.org/ebooks/2162.epub.noimages"
            ),

            ViaHTTP(
                title="Marriage and Love",
                url="https://www.gutenberg.org/ebooks/20715.epub.noimages"
            ),

            ViaHTTP(
                title="The Place of the Individual in Society",
                url="https://www.gutenberg.org/ebooks/71418"
            )
        ]
    )


    nietzsche = Author(
        name="Friedrich Nietzsche",
        books_via_scraper=[
            ViaScraper(
                title="Thus Spake Zarathustra",
                url="https://www.gutenberg.org/files/1998/1998-h/1998-h.htm",
                initial_marker="ZARATHUSTRA’S DISCOURSES.",
                terminal_marker="APPENDIX"
            ),

            ViaScraper(
                title="Beyond Good and Evil",
                url="https://www.gutenberg.org/cache/epub/4363/pg4363-images.html",
                initial_marker="CHAPTER I. ",
                terminal_marker="FROM THE HEIGHTS"
            ),

            ViaScraper(
                title="The Genealogy of Morals",
                url="https://www.gutenberg.org/cache/epub/52319/pg52319-images.html",
                initial_marker="FIRST ESSAY.",
                terminal_marker="betray us!"
            ),

            ViaScraper(
                title="The Antichrist",
                url="https://www.gutenberg.org/cache/epub/19322/pg19322-images.html",
                initial_marker="PREFACE",
                terminal_marker="THE END"
            ),

            ViaScraper(
                title="Human, All Too Human",
                url="https://www.gutenberg.org/cache/epub/38145/pg38145-images.html",
                initial_marker="PREFACE.",
                terminal_marker="sinfulness."
            ),

            ViaScraper(
                title="Ecce Homo",
                url="https://www.gutenberg.org/cache/epub/52190/pg52190-images.html",
                initial_marker="PREFACE.",
                terminal_marker="It really seems that we have a path."
            ),


        ]
    )


    rumi = Author(
        name="Jalāl al-Dīn Muḥammad Rūmī",
        books_via_scraper=[
            ViaScraper(
                title="The Mesnevi",
                url="https://www.gutenberg.org/cache/epub/61724/pg61724-images.html",
                initial_marker="THE ACTS OF THE ADEPTS",
                terminal_marker="God best knows what is right."
            )
        ]
    )


    kropotkin = Author(
        name="Peter (Pyotr) Kropotkin",
        books_via_scraper=[
            ViaScraper(
                title="Mutual Aid: A Factor of Evolution",
                url="https://www.gutenberg.org/cache/epub/4341/pg4341-images.html",
                initial_marker="Two aspects",
                terminal_marker="our race"
            ),

            ViaScraper(
                title="The Conquest of Bread",
                url="https://www.gutenberg.org/cache/epub/23428/pg23428-images.html",
                initial_marker="OUR RICHES",
                terminal_marker="Social Revolution."
            )
        ]

    )


    bakunin = Author(
        name="Mikhail Bakunin",
        books_via_scraper=[
            ViaScraper(
                title="God and the State",
                url="https://www.gutenberg.org/cache/epub/36568/pg36568-images.html",
                initial_marker="Elisée Reclus.",
                terminal_marker="Genius of Christianity"
            )
        ]
    )


    proudhon = Author(
        name="Pierre-Joseph Proudhon",
        books_via_scraper=[
            ViaScraper(
                title="What is Property? An Inquiry into the Principle of Right and of Government",
                url="https://www.gutenberg.org/cache/epub/360/pg360-images.html",
                initial_marker="FIRST MEMOIR.",
                terminal_marker="and absurd."
            ),

            ViaScraper(
                title="System of Economical Contradictions; Or, The Philosophy of Misery",
                url="https://www.gutenberg.org/cache/epub/444/pg444-images.html",
                initial_marker="Before entering",
                terminal_marker="reason of our existence."
            )
        ]

    )
    

    berkman = Author(
        name="Alexander Berkman",
        books_via_scraper=[
            ViaScraper(
                title="Prison Memoirs of an Anarchist",
                url="https://www.gutenberg.org/cache/epub/34406/pg34406-images.html",
                initial_marker="The Call of Homestead",
                terminal_marker="I have found work to do."
            ),

            ViaScraper(
                title="Deportation - Its Meaning & Menace",
                url="https://www.gutenberg.org/cache/epub/68442/pg68442-images.html",
                initial_marker="DEPORTATION—Its Meaning and Menace",
                terminal_marker="but also of reward."
            )
        ]
    )


    sun_tzu = Author(
        name="Sun Tzu",
        books_via_http=[
            ViaHTTP(
                title="The Art of War",
                url="https://sites.ualberta.ca/~enoch/Readings/The_Art_Of_War.pdf",
                start_page=3,
                end_page=65
            )
        ]
    )

    return [
        marx, mao, lenin, garvey, gandhi, yat_sen, goldman, kropotkin, rizal, rumi, nietzsche, 
        bakunin, proudhon, berkman, sun_tzu, vivekananda, rai, blavatsky 
    ] 


if __name__ == "__main__":
    for author in prepare_sources():
        author.download_books()               
        logger.info("Next author...")

