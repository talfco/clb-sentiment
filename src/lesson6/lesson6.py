from govSocialMediaAnalyzer import GovernmentSocialMediaAnalyzer

def main():
    analyzer_ch = GovernmentSocialMediaAnalyzer("CH")
    gov_df = analyzer_ch.create_govapi_politican_table()
    tw_df = analyzer_ch.create_tw_politican_table(gov_df)
    analyzer_ch.create_tw_party_table(tw_df)


if __name__ == '__main__':
    main()
