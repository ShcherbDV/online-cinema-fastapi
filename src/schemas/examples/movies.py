movie_item_schema_example = {
    "id": 9933,
    "name": "The Swan Princess: A Royal Wedding",
    "year": "2020",
    "imdb": 70,
    "overview": "Princess Odette and Prince Derek are going to a wedding at Princess Mei Li and her beloved Chen. "
                "But evil forces are at stake and the wedding plans are tarnished and "
                "true love has difficult conditions."
}

movie_list_response_schema_example = {
    "movies": [
        movie_item_schema_example
    ],
    "prev_page": "/cinema/movies/?page=1&per_page=1",
    "next_page": "/cinema/movies/?page=3&per_page=1",
    "total_pages": 9933,
    "total_items": 9933
}
