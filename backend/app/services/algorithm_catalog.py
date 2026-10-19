"""Initial in-memory catalog used before the database layer is introduced."""

from collections.abc import Iterable

from app.schemas.algorithm import AlgorithmDetail, AlgorithmSummary


_CATALOG: dict[str, AlgorithmDetail] = {
    "maximum-in-list": AlgorithmDetail(
        slug="maximum-in-list",
        title="Поиск максимума в списке",
        category="Обработка последовательностей",
        difficulty="Начальный",
        short_description=(
            "Поиск наибольшего значения в непустой последовательности "
            "натуральных чисел."
        ),
        description=(
            "Алгоритм последовательно просматривает элементы списка и хранит "
            "текущий максимум. Корректность основывается на инварианте: после "
            "обработки префикса текущий максимум не меньше каждого элемента "
            "этого префикса."
        ),
        input_data="Непустой список натуральных чисел.",
        output_data="Натуральное число — максимум входного списка.",
        preconditions="Входной список содержит хотя бы один элемент.",
        postconditions=(
            "Каждый элемент входного списка не больше результата алгоритма. "
            "Это свойство формально доказано в текущей версии."
        ),
        invariant_description=(
            "После обработки первых i элементов переменная maximum равна "
            "максимуму обработанного префикса."
        ),
        pseudocode=(
            "maximum ← first(values)\n"
            "for each value in values after first(values):\n"
            "    if value > maximum:\n"
            "        maximum ← value\n"
            "return maximum"
        ),
        default_proof=(
            "by\n"
            "  exact member_le_maximumFrom initial value tail membership\n"
        ),
    ),
    "linear-search": AlgorithmDetail(
        slug="linear-search",
        title="Линейный поиск",
        category="Поиск",
        difficulty="Начальный",
        short_description=(
            "Последовательный поиск значения в списке с проверкой "
            "корректности найденного индекса."
        ),
        description=(
            "Алгоритм проверяет элементы списка слева направо. Формальная "
            "спецификация связывает успешный результат с существованием "
            "искомого значения по возвращённому индексу."
        ),
        input_data="Список натуральных чисел и искомое натуральное число.",
        output_data=(
            "Индекс найденного элемента или специальное значение, "
            "обозначающее отсутствие элемента."
        ),
        preconditions="Дополнительные предусловия отсутствуют.",
        postconditions=(
            "Если возвращён индекс, элемент по нему равен искомому значению; "
            "если элемент не найден, искомое значение отсутствует в списке."
        ),
        invariant_description=(
            "Перед проверкой элемента с индексом i искомое значение "
            "отсутствует в префиксе длины i."
        ),
        pseudocode=(
            "for index, value in enumerate(values):\n"
            "    if value = target:\n"
            "        return index\n"
            "return not_found"
        ),
        default_proof="by\n  simp\n",
    ),
}


def list_algorithms() -> Iterable[AlgorithmSummary]:
    """Return catalog cards in stable title order."""

    return sorted(
        (
            AlgorithmSummary(
                slug=algorithm.slug,
                title=algorithm.title,
                category=algorithm.category,
                short_description=algorithm.short_description,
                difficulty=algorithm.difficulty,
            )
            for algorithm in _CATALOG.values()
        ),
        key=lambda algorithm: algorithm.title,
    )


def get_algorithm(slug: str) -> AlgorithmDetail | None:
    """Find an algorithm by public slug."""

    return _CATALOG.get(slug)
