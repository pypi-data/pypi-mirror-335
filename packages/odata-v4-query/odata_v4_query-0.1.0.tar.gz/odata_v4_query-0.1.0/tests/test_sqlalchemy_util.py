import pytest
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from odata_v4_query.errors import (
    NoRootClassFound,
    ParseError,
    UnexpectedNullOperand,
)
from odata_v4_query.filter_parser import FilterNode
from odata_v4_query.query_parser import ODataQueryOptions, ODataQueryParser
from odata_v4_query.utils.sqlalchemy import apply_to_sqlalchemy_query, get_query_root_cls

from ._core.sqlalchemy import User, get_engine, seed_data


@pytest.fixture(scope='session')
def session():
    engine = get_engine()
    with Session(engine) as session:
        seed_data(session)
        yield session


class TestSQLAlchemy:

    parser = ODataQueryParser()

    def test_skip(self, session: Session):
        query = select(User)
        users_count = len(session.scalars(query).all())
        options = self.parser.parse_query_string('$skip=2')
        query = apply_to_sqlalchemy_query(options, query)
        result = session.scalars(query).all()
        assert len(result) == users_count - 2
        assert result[0].name == 'Alice'

    def test_top(self, session: Session):
        options = self.parser.parse_query_string('$top=2')
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 2
        assert result[0].name == 'John'
        assert result[1].name == 'Jane'

    def test_filter(self, session: Session):
        # comparison and logical
        options = self.parser.parse_query_string(
            "$filter=name eq 'John' and age ge 25"
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 1
        assert result[0].name == 'John'

        options = self.parser.parse_query_string(
            '$filter=age lt 25 or age gt 35'
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 4

        options = self.parser.parse_query_string(
            "$filter=name in ('Eve', 'Frank')"
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 2
        assert result[0].name == 'Eve'
        assert result[1].name == 'Frank'

        options = self.parser.parse_query_string(
            "$filter=name nin ('Eve', 'Frank')"
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 8

        options = self.parser.parse_query_string(
            "$filter=name ne 'John' and name ne 'Jane'"
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 8

        options = self.parser.parse_query_string(
            "$filter=not name eq 'John' and not name eq 'Jane'"
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 8

        options = self.parser.parse_query_string('$filter=name eq null')
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 0

        options = self.parser.parse_query_string('$filter=name ne null')
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 10

        # string functions
        options = self.parser.parse_query_string(
            "$filter=startswith(name, 'J') and age ge 25"
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 2
        assert result[0].name == 'John'
        assert result[1].name == 'Jane'

        options = self.parser.parse_query_string(
            "$filter=endswith(name, 'e')"
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 5
        assert result[0].name == 'Jane'
        assert result[1].name == 'Alice'
        assert result[2].name == 'Charlie'
        assert result[3].name == 'Eve'
        assert result[4].name == 'Grace'

        options = self.parser.parse_query_string(
            "$filter=contains(name, 'i') and age le 35"
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 2
        assert result[0].name == 'Alice'
        assert result[0].age == 35
        assert result[1].name == 'Charlie'
        assert result[1].age == 32

        # collection
        options = self.parser.parse_query_string(
            "$filter=addresses has '101 Main St'"
        )
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 2
        assert result[0].name == 'Alice'
        assert result[1].name == 'Bob'

    def test_search(self, session: Session):
        options = self.parser.parse_query_string('$search=John')
        query = apply_to_sqlalchemy_query(
            options, User, search_fields=['name', 'email']
        )
        result = session.scalars(query).all()
        assert len(result) == 1
        assert result[0].name == 'John'

    def test_orderby(self, session: Session):
        options = self.parser.parse_query_string('$orderby=name asc,age desc')
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).all()
        assert len(result) == 10
        assert result[0].name == 'Alice'
        assert result[1].name == 'Bob'
        assert result[1].age == 40
        assert result[2].name == 'Bob'
        assert result[2].age == 28
        assert result[3].name == 'Charlie'
        assert result[4].name == 'David'
        assert result[5].name == 'Eve'
        assert result[6].name == 'Frank'
        assert result[7].name == 'Grace'
        assert result[8].name == 'Jane'
        assert result[9].name == 'John'

    def test_expand(self, session: Session):
        options = self.parser.parse_query_string('$expand=posts')
        query = apply_to_sqlalchemy_query(options, User)
        result = session.scalars(query).unique().all()
        assert result[0].posts[0].title == 'Post 1'
        assert result[0].posts[1].title == 'Post 2'
        assert result[1].posts[0].title == 'Post 3'
        assert result[1].posts[1].title == 'Post 4'

    def test_select(self, session: Session):
        options = self.parser.parse_query_string('$select=name,email')
        query = apply_to_sqlalchemy_query(options, User)
        result = session.execute(query).all()
        assert len(result) == 10
        assert result[0][0] == 'John'
        assert result[0][1] == 'john@example.com'

    def test_error(self):
        # unexpected null filters
        with pytest.raises(ParseError):
            options = ODataQueryOptions(filter_=FilterNode(type_='value'))
            apply_to_sqlalchemy_query(options, User)

        # null left or right operands
        with pytest.raises(UnexpectedNullOperand):
            options = ODataQueryOptions(
                filter_=FilterNode(type_='operator', value='eq')
            )
            apply_to_sqlalchemy_query(options, User)

        # null left or right values
        with pytest.raises(UnexpectedNullOperand):
            options = ODataQueryOptions(
                filter_=FilterNode(
                    type_='operator',
                    value='eq',
                    left=FilterNode(type_='identifier'),
                    right=FilterNode(type_='literal', value='John'),
                )
            )
            apply_to_sqlalchemy_query(options, User)

        # null list arguments
        with pytest.raises(UnexpectedNullOperand):
            options = ODataQueryOptions(
                filter_=FilterNode(
                    type_='operator',
                    value='in',
                    left=FilterNode(type_='identifier', value='name'),
                    right=FilterNode(type_='list'),
                )
            )
            apply_to_sqlalchemy_query(options, User)

        # null operand for has operator
        with pytest.raises(UnexpectedNullOperand):
            options = ODataQueryOptions(
                filter_=FilterNode(
                    type_='operator',
                    value='has',
                    left=FilterNode(type_='identifier', value='addresses'),
                    right=FilterNode(type_='literal'),
                )
            )
            apply_to_sqlalchemy_query(options, User)

        # null operand for and/or operator
        with pytest.raises(UnexpectedNullOperand):
            options = ODataQueryOptions(
                filter_=FilterNode(type_='operator', value='and')
            )
            apply_to_sqlalchemy_query(options, User)

        # null operand for not/nor operator
        with pytest.raises(UnexpectedNullOperand):
            options = ODataQueryOptions(
                filter_=FilterNode(type_='operator', value='not')
            )
            apply_to_sqlalchemy_query(options, User)

        # unknown operator
        with pytest.raises(ParseError):
            options = ODataQueryOptions(
                filter_=FilterNode(type_='operator', value='unknown')
            )
            apply_to_sqlalchemy_query(options, User)

        # null function
        with pytest.raises(ParseError):
            options = ODataQueryOptions(filter_=FilterNode(type_='function'))
            apply_to_sqlalchemy_query(options, User)

        # null function arguments
        with pytest.raises(ParseError):
            options = ODataQueryOptions(
                filter_=FilterNode(type_='function', value='startswith')
            )
            apply_to_sqlalchemy_query(options, User)

        # more than 2 function arguments
        with pytest.raises(ParseError):
            options = ODataQueryOptions(
                filter_=FilterNode(
                    type_='function',
                    value='startswith',
                    arguments=[
                        FilterNode(type_='identifier', value='name'),
                        FilterNode(type_='literal', value='J'),
                        FilterNode(type_='literal', value='J'),
                    ],
                )
            )
            apply_to_sqlalchemy_query(options, User)

        # null function operand
        with pytest.raises(ParseError):
            options = ODataQueryOptions(
                filter_=FilterNode(
                    type_='function',
                    value='startswith',
                    arguments=[
                        FilterNode(type_='identifier', value='name'),
                        FilterNode(type_='literal'),
                    ],
                )
            )
            apply_to_sqlalchemy_query(options, User)

        # unknown function
        with pytest.raises(ParseError):
            options = ODataQueryOptions(
                filter_=FilterNode(
                    type_='function',
                    value='unknown',
                    arguments=[
                        FilterNode(type_='identifier', value='name'),
                        FilterNode(type_='literal', value='J'),
                    ],
                )
            )
            apply_to_sqlalchemy_query(options, User)

        # no root class found cases
        query = select(func.count('*'))
        with pytest.raises(ValueError):
            get_query_root_cls(query, raise_on_none=True)
        with pytest.raises(NoRootClassFound):
            options = self.parser.parse_query_string('$filter=name eq null')
            apply_to_sqlalchemy_query(options, query)
        with pytest.raises(NoRootClassFound):
            options = self.parser.parse_query_string('$search=John')
            apply_to_sqlalchemy_query(options, query, search_fields=['name'])
        with pytest.raises(NoRootClassFound):
            options = self.parser.parse_query_string('$orderby=name asc')
            apply_to_sqlalchemy_query(options, query)
        with pytest.raises(NoRootClassFound):
            options = self.parser.parse_query_string('$expand=posts')
            apply_to_sqlalchemy_query(options, query)
        with pytest.raises(NoRootClassFound):
            options = self.parser.parse_query_string('$select=name,email')
            apply_to_sqlalchemy_query(options, query)
