*** Variables ***
#${API_ENDPOINT}	https://informationplatform.ul.com	#For PROD basic
${API_ENDPOINT}	https://io.ul.com/InformationPlatform  #For PROD OAuth2

#@{database}  pymysql    infopltfrm_transDBv07  ul_transUser    29LPMW6Ljv  usnbkinpt018d.global.ul.com    3316	#DB for DEV
#
#${db}         @{database}[1]
#${user}       @{database}[2]
#${pass_wd}    @{database}[3]
#${host}       @{database}[4]
#${port}       @{database}[5]


${user_name}    ipprdusr    #for PROD
${password}     8XHaBW#f@DnX3]P$#   #for PROD

#OAuth 2
${AUTH_ENDPOINT}        https://login.microsoftonline.com/ul.onmicrosoft.com/oauth2/token
${Grant_Type}           client_credentials
${Client_ID}            98da3396-91da-4bf4-8e6c-62ba7a32ba7a
${Client_Secret}        _s~06RK67yvVhc-QgqTfsR0Gwaf5vs~8.U
${Scope}                User.Read

#${Api_ver}  5.30

${certificate_hierarchy_Id}     f9545519-3205-426d-9086-416a94925e75           #for PROD
${certificate2_hierarchy_Id}    73f7dbcb-1417-44c4-902f-4c2ffe7129bb           #for PROD
#${certificate3_hierarchy_Id}
${certificate_metadataId}       d03bac94-d0c1-400b-aa82-19000c8c43d3           #for PROD
${certificate2_metadataId}      7fa4743e-6134-4d57-a287-256b0cf3be97           #for PROD
#${certificate3_metadataId}
${standard_hierarchy_Id}	ge28b891-a43e-4f59-9f15-2554f93359fe               #for PROD - with clause group
${standard_hierarchy_Id}	14f8ddd8-afa2-48f4-8234-88698628c44c               #for DEV - no clause group
${Reg_prod1_metadataId} 	cbe97212-51fa-471d-be0d-9267de56f5d3               #for PROD
${Reg_prod2_metadataId} 	9529e43d-b202-44f8-89da-9d1e1c265786               #for PROD
${Reg_prod3_metadataId} 	47350fbb-0c48-4995-8581-2c42c92a2e47               #for PROD
${noEvalReqd_hierarchy_Id}     ge28b891-a43e-4f59-9f15-2554f93359fe            #for PROD  cee668aa-cfda-4191-8d55-b4c0ead85da3 DEV
${regression_product_1_hierarchy_id}    cd2ada96-0201-436b-8238-3de7299be82e   #for PROD
${regression_product_2_hierarchy_id}    238b9baf-97bd-4197-aa1b-ade2a3b5d238   #for PROD
${regression_product_3_hierarchy_id}    6b58c770-424c-46bf-86b6-0f608bf58d20   #for PROD

${certificate_hierarchy_IdV2.1}     6b6db87e-3115-4455-8ad3-f874e896a977       #for DEV
${certificate_metadataIdV2.1}       ee7c7e90-b095-49a0-8335-cea95f2339ab       #for DEV
${certificate_hierarchy_IdV2.2}     8d191dcf-ce02-49df-a069-c71749ff1d31       #for DEV
${certificate_metadataIdV2.2}       7543eca8-65a1-460e-9caa-f210f58540a6       #for DEV
${Validation_standard_Id}	        172d5c17-85ed-11e9-9323-005056ac4531       #for DEV
${Validation_standardLabel_Id}	    a589a6b9-875f-11e9-9323-005056ac4531       #for DEV
${Validation_standardLabel2_Id}	    91fe8ebe-89f0-11e9-9323-005056ac4531       #for DEV