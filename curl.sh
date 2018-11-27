#BEAR_TOKEN='Authorization: Bearer Atza|IwEBIIKSXl5MQVD6xmskLlvO8Pugxrr-8tBhslII2dy6uStzkWFzQzcTW9wk7-8xBdsSddDMXkSbrkbAMGlcd1hWI69Cw1rouMPofId7Qb4n58wyjhq1Y5NQnBTUCYwcBZmmzMrfhsHjicxo5uU7kTuyVf_p9c32guzdnEORTsfhevSiikEw6AiQnrDqjMTzGFR4gy662BQWuWTc_zqCv7mwY0jx7i2Zv_Qk9NkWKPlilv-eOnr5AfwKVknUKHH8grH84AOH7syTSv_VIv5lBBtz46nnEM24VB3tukHydAcp0XPwATAAx83gnIA1nLzIsGT5svOAwzj7_ZuFh-7oFF0n97OibPFoaH_JrOC-maaahZlRzBCe6HjhSKc_isAc1esa8zxiTxrV3GYVC5KRVZ-fKko2pmr_aPGBKO_Xo5l5f5vTxGdvebnnU4cmqxinvtrVMB39tKoa1r2qSRJUTvKDs2QvxGmMVbwUPbpL85BhBTC6V6RU1MfxaJN25C9SIkZjWBg'
#URL=https://drive.amazonaws.com/drive/v1/account/endpoint

if [ $# -gt 0 ]; then
	METHOD="PUT"
	URL="https://lb9911.hubic.ovh.net/v1/AUTH_773ddc9402d55f6dd47e9c536c826de3/default/Documents/Books/"
	echo  sending "$METHOD" "$URL"

	#-H "X-Container-Meta-Access-Control-Expose-Headers: Access-Control-Allow-Origin"
	#curl -v -X PUT  -H "X-Auth-Token: 39c63501109e4e0f9e57a2ec56fc86f4" -H "X-Container-Meta-Access-Control-Allow-Origin: https://albertdupre.byethost13.com" -H "X-Container-Meta-Access-Control-Expose-Headers: Access-Control-Allow-Origin" $URL
	#curl -v -X OPTIONS  -H "X-Auth-Token: b2e5894a1f354be7846ab92314a487e9" -H "Origin: https://albertdupre.byethost13.com" $URL
	curl -v -X OPTIONS  -H "X-Auth-Token: b2e5894a1f354be7846ab92314a487e9" $URL
	#'file=@'$1


fi

#echo


