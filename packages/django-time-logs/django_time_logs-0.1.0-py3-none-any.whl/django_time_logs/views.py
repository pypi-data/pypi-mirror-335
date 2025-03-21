from dateutil.parser import parse
from django.conf import settings
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from elasticsearch_dsl import Q, Search, A
from elasticsearch_dsl.query import Q as EQ

from django_time_logs.utils import get_elastic_client


@staff_member_required
def time_logs(request):
    """ List time logs """
    try:
        template_name = settings.TIME_LOG_TEMPLATE
    except Exception as e:
        print("template is not defined in settings. Switching to default template")
        template_name = 'django_time_logs/time_logs.html'

    try:
        index_name = settings.TIME_LOGGER_INDEX
    except Exception as e:
        return render(request, template_name, {"error": "Kindly set TIME_LOGGER_INDEX in your .env"})

    created_start = request.GET.get("start_date", None)
    created_end = request.GET.get("end_date", None)
    title = request.GET.get("title", None)
    duration = request.GET.get("duration", None)
    q_search = request.GET.get("q", None)
    if q_search:
        q_search = f'*{q_search}*'
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '-created')
    size = request.GET.get('size', 100)
    delete = request.GET.get('delete', None)
    try:
        size = int(size)
    except:
        size = 100

    es_client = get_elastic_client()
    time_logs = Search(using=es_client, index=index_name)
    titles = Search(using=es_client, index=index_name).extra(collapse={"field": "title.keyword"})

    time_logs = time_logs.filter(EQ('match', title=title)) if title else time_logs
    time_logs = time_logs.filter(EQ('match', duration=duration)) if duration else time_logs
    time_logs = time_logs.filter('range', created={'gte': parse(created_start)}) if created_start else time_logs
    time_logs = time_logs.filter('range', created={'lte': parse(created_end)}) if created_end else time_logs
    time_logs = time_logs.sort(sort) if sort else time_logs
    time_logs = time_logs.query('wildcard', title={'value': q_search, 'case_insensitive': True}) if q_search else time_logs

    if delete:
        time_logs = time_logs.to_dict()
        if time_logs:
            es_client.delete_by_query(
                index=index_name,
                body={"query": time_logs["query"]}
            )
            # Fetch new
            time_logs = Search(using=es_client, index=index_name).sort('-created')
            titles = Search(using=es_client, index=index_name).extra(collapse={"field": "title.keyword"})
    

    time_logs = time_logs.execute()

    # paginate time logs begins here
    if not (size and isinstance(size, int)):
        size = 100
    paginator = Paginator(time_logs, size) #100 items per page
    try:
        time_logs = paginator.page(page)
    except PageNotAnInteger:
        time_logs = paginator.page(1)
    except EmptyPage:
        time_logs = paginator.page(paginator.num_pages)
    # end of pagination

    context = {
        'titles': titles,
        'time_logs': time_logs,
        'sorts':['duration', 'created', '-duration', '-created']
    }
    # return JsonResponse(context, safe=False)
    return render(request, template_name, context)