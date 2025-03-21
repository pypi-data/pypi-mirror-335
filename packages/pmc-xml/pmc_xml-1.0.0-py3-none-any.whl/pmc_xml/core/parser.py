import os
import datetime
from collections import defaultdict

try:
    import lxml.etree as ET
except ImportError:
    import xml.etree.cElementTree as ET

import click
from simple_loggers import SimpleLogger

from pmc_xml import util
from pmc_xml.core.article import ArticleObject
from pmc_xml.core.abstract import parse_abstract
 


def parse_tree(tree):
    if tree.find('article') is None:
        yield None
    else:
        for article in tree.iterfind('article'):
            context = {}

            front = article.find('front')
            article_meta = front.find('article-meta')
            journal_meta = front.find('journal-meta')
            
            context['pmc'] = 'PMC' + article_meta.findtext('article-id[@pub-id-type="pmc"]')
            context['doi'] = article_meta.findtext('article-id[@pub-id-type="doi"]')
            context['pmid'] = article_meta.findtext('article-id[@pub-id-type="pmid"]')
            # print(context['pmc'])

            issn = journal_meta.find('issn[@pub-type="ppub"]')
            if issn is None:
                issn = journal_meta.find('issn')
            e_issn = journal_meta.find('issn[@pub-type="epub"]')
            if e_issn is None:
                e_issn = journal_meta.find('issn')

            context['e_issn'] = e_issn.text if e_issn is not None else '.'
            context['issn'] = issn.text if issn is not None else '.'

            article_title = article_meta.find('title-group/article-title')
            context['title'] = ''.join(article_title.itertext()).strip().replace('\n', ' ')

            context['journal'] = journal_meta.findtext('journal-title-group/journal-title')
            context['iso_abbr'] = journal_meta.findtext('journal-id[@journal-id-type="iso-abbrev"]')
            context['med_abbr'] = journal_meta.findtext('journal-id[@journal-id-type="nlm-ta"]')

            pub_date_path_list = [
                'pub-date[@pub-type="epub"]', 
                'pub-date[@date-type="pub"]', 
                'pub-date[@pub-type="pmc-release"]',    
                'pub-date[@pub-type="ppub"]', 
            ]
            for pub_date_path in pub_date_path_list:
                pubdate = article_meta.find(pub_date_path)
                if pubdate is not None:
                    break
            
            if pubdate is not None:
                year = pubdate.findtext('year')
                month = pubdate.findtext('month') or '1'
                day = pubdate.findtext('day') or '1'
            else:
                pub_date = article_meta.find('pub-date')
                year = pub_date.findtext('year')
                month = pub_date.findtext('month') or '1'
                day = pub_date.findtext('day') or '1'

            context['year'] = year
            context['pubdate'] = datetime.datetime(int(year), int(month), int(day)).strftime('%Y/%m/%d')
            context['pubmed_pubdate'] = context['pubdate']

            context['pagination'] = article_meta.findtext('elocation-id')
            context['volume'] = article_meta.findtext('volume')
            context['issue'] = article_meta.findtext('issue')

            context['keywords'] = [kwd for kwd in article_meta.xpath('kwd-group/kwd/text()') if kwd.strip()]
            context['pub_status'] = '.' # do not know which field to use

            context['abstract'] = parse_abstract(article_meta.findall('abstract')).strip()
            

            article_type = article.attrib.get('article-type')
            context['pub_types'] = [article_type]  # do not know which field to use

            # author emails
            cor_email_map = {}
            cor_list = article_meta.findall('author-notes/corresp')
            for cor in cor_list:
                cor_id = cor.attrib.get('id')
                if cor_id:
                    email = cor.findtext('email')
                    cor_email_map[cor_id] = email

            # authors
            author_list = []
            author_mail = []
            aff_author_map = defaultdict(list)
            for author in article_meta.findall('contrib-group/contrib[@contrib-type="author"]'):
                last_name = author.findtext('name/surname')
                fore_name = author.findtext('name/given-names')
                author_name = ' '.join(name for name in [fore_name, last_name] if name)
                if author_name:
                    author_list.append(author_name)

                for aff in author.findall('xref[@ref-type="aff"]'):
                    aff_id = aff.attrib['rid']
                    aff_author_map[aff_id].append(author_name)

                for cor in author.findall('xref[@ref-type="other"]'):
                    cor_id = cor.attrib['rid']
                    email = cor_email_map.get(cor_id)
                    if email:
                        mail = '{}: {}'.format(author_name, email)
                        author_mail.append(mail)

            context['authors'] = author_list

            context['author_mail'] = '.'
            if not author_mail:
                corresp = article_meta.find('author-notes/corresp')
                if corresp is not None:
                    context['author_mail'] = ''.join(corresp.itertext()).strip()
            else:
                context['author_mail'] = author_mail

            context['author_first'] = context['author_last'] = '.'
            if author_list:
                context['author_first'] = author_list[0]
                if len(author_list) > 1:
                    context['author_last'] = author_list[-1]

            # affiliations
            aff_list = []
            for n, aff in enumerate(article_meta.findall('contrib-group/aff'), 1):
                aff_text = ''.join(aff.itertext()).replace('\n', ' ')[1:]
                aff_authors = aff_author_map.get(aff.attrib['id'])
                aff_list.append(f'{n}. {aff_text} - {aff_authors}')
            context['affiliations'] = aff_list

            yield context


class PMC_XML_Parser(object):
    """PMC XML Parser
    >>> from PMC_xml import PMC_XML_Parser
    >>> pmc = PMC_XML_Parser()
    >>> for article in pmc.parse('30003000'):
    >>>     print(article)
    """

    def __init__(self):
        self.logger = SimpleLogger('PMC_XML_Parser')

    def get_tree(self, xml):
        if os.path.isfile(xml):
            tree = ET.parse(util.safe_open(xml))
        elif xml.startswith('<?xml '):
            tree = ET.fromstring(xml)
        else:
            tree = ET.fromstring(util.get_pmc_xml(xml))
        return tree

    def parse(self, xml):
        """parse xml from local file or text string
        """
        try:
            tree = self.get_tree(xml)
        except Exception as e:
            raise Exception(click.style(f'[XML_PARSE_ERROR] {e}', fg='red'))
        
        for context in parse_tree(tree):
            yield ArticleObject(**context)
