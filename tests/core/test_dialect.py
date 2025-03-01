from sqlglot import exp, parse_one

from sqlmesh.core.dialect import (
    Jinja,
    Model,
    format_model_expressions,
    parse,
    text_diff,
)


def test_format_model_expressions():
    x = format_model_expressions(
        parse(
            """
    MODEL(name a.b, kind full)
    ;

    @DEF(x
    , 1);

    SELECT
    CAST(a AS int),
    CAST(b AS int) AS b,
    CAST(c + 1 AS int) AS c,
    d::int,
    e::int as e,
    (f + 1)::int as f,
    sum(g + 1)::int as g,
    CAST(h AS int), -- h
    CAST(i AS int) AS i, -- i
    CAST(j + 1 AS int) AS j, -- j
    k::int, -- k
    l::int as l, -- l
    (m + 1)::int as m, -- m
    sum(n + 1)::int as n, -- n
    o,
    p + 1,
    """
        )
    )
    assert (
        x
        == """MODEL (
  name a.b,
  kind FULL
);

@DEF(x, 1);

SELECT
  a::INT AS a,
  b::INT AS b,
  CAST(c + 1 AS INT) AS c,
  d::INT AS d,
  e::INT AS e,
  (
    f + 1
  )::INT AS f,
  SUM(g + 1)::INT AS g,
  h::INT AS h, /* h */
  i::INT AS i, /* i */
  CAST(j + 1 AS INT) AS j, /* j */
  k::INT AS k, /* k */
  l::INT AS l, /* l */
  (
    m + 1
  )::INT AS m, /* m */
  SUM(n + 1)::INT AS n, /* n */
  o AS o,
  p + 1"""
    )

    x = format_model_expressions(
        parse(
            """
            MODEL(name a.b, kind FULL);
            SELECT * FROM x WHERE y = {{ 1 }};"""
        )
    )
    assert (
        x
        == """MODEL (
  name a.b,
  kind FULL
);

SELECT * FROM x WHERE y = {{ 1 }};"""
    )


def test_macro_format():
    assert parse_one("@EACH(ARRAY(1,2), x -> x)").sql() == "@EACH(ARRAY(1, 2), x -> x)"


def test_format_body_macros():
    assert (
        format_model_expressions(
            parse(
                """
    Model ( name foo );
    @WITH(TRUE) x AS (SELECT 1)
    SELECT col::int
    FROM foo @ORDER_BY(@include_order_by)
    @EACH( @columns,
    item -> @'@iteaoeuatnoehutoenahuoanteuhonateuhaoenthuaoentuhaeotnhaoem'),      @'@foo'
    """
            )
        )
        == """MODEL (
  name foo
);

@WITH(TRUE) x AS (
  SELECT
    1
)
SELECT
  col::INT AS col
FROM foo
@ORDER_BY(@include_order_by)
  @EACH(@columns, item -> @'@iteaoeuatnoehutoenahuoanteuhonateuhaoenthuaoentuhaeotnhaoem'),
  @'@foo'"""
    )


def test_text_diff():
    assert """@@ -1,3 +1,3 @@

 SELECT
-  *
-FROM x
+  1
+FROM y""" in text_diff(
        parse_one("SELECT * FROM x"), parse_one("SELECT 1 FROM y")
    )


def test_parse():
    expressions = parse(
        """
        MODEL (
            kind full,
            dialect "hive",
        );

        CACHE TABLE x as SELECT 1 as Y;

        SELECT * FROM x WHERE y = {{ 1 }} ;
    """
    )

    assert isinstance(expressions[0], Model)
    assert isinstance(expressions[1], exp.Cache)
    assert isinstance(expressions[2], Jinja)
