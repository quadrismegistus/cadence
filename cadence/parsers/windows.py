# # def iter_windows(df,window_len=3):
# #     for linedf in iter_lines(df):
# #         for combodf in iter_combos(linedf):
# #             ldf=combodf.reset_index()
# #             ldf = ldf[ldf.word_ipa!=""]
# #             display(ldf)
# #             indices=list(range(len(ldf)))
# #             for indnow in slices(indices,window_len):
# #                 dfslice=combodf.iloc[indnow[0] : indnow[-1]+1]
# #                 display(dfslice)
# #                 stop
                

# # def iter_windows(df,window_len=3):
# #     for linedf in iter_lines(df):
# #         for combodf in iter_combos(linedf):
# #             ldf=combodf.reset_index()
# #             linedf_nopunc = ldf[ldf.word_ipa!=""]
# #             linewords=[y for x,y in sorted(linedf_nopunc.groupby('word_i'))]        
# #             for lwi,lineword_slice in enumerate(slices(linewords,window_len)):
# #                 for wi,word_combo in enumerate(apply_combos(pd.concat(lineword_slice), 'word_i', 'word_ipa_i', combo_key='word_combo_i')):
# #                     word_combo['word_window_i']=lwi
# #                     yield word_combo

            
            
# # #             for lwi,lineword_slice in enumerate(slices(linewords,window_len)):
# # #                 for wi,word_combo in enumerate(apply_combos(pd.concat(lineword_slice), 'word_i', 'word_ipa_i', combo_key='word_combo_i')):
# # #                     word_combo['word_window_i']=lwi
# # #                     yield word_combo



# def iter_parsed_windows(df):
#     for window in iter_windows(df):
#         for parsed in iter_parsed(window):
#             yield parsed


# def get_parsed_windows(txtdf):
#     # get all combos
#     return pmap_groups(
#         iter_parsed_windows,
#         txtdf.groupby(['stanza_i','line_i']),
#         progress=True,
#         num_proc=7,
#         desc='Parsing all windows'
#     )



