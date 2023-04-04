# **Roided Holehe OSINT**

This is Roided Holehe OSINT. A python program that runs on top of Holehe OSINT. Roided Holehe allows you to check multiple emails existence in multiple websites. For further information about Holehe check https://github.com/megadose/holehe.

Author: **Ishfaq Ahmed**  
Based On: **Holehe OSINT by [megadose](https://github.com/megadose)**

---

### **How to use**:

1.  Run app.exe in 'dist/app'.
2.  Copy the path to your file and paste it when the program asks for the file. The input file should contain the emails on a column with a header and the file type be .xlsx.
3.  Only the valid emails from the column will be processed so you don't need to check for invalid values.
4.  Once the program ends, the file will be saved to a folder "RoidedHolehe" in your documents folder.
5.  If the results have too many rate_limit as 'true' then change your ip address and re-run the program with only rate_limit='true'.

### **Adding Custom modules**

To mitigate the missing crm modules that holehe doesnt have and if any holehe modules need fixing. More details can be found here.

#### 1. Fix pipedrive module:

**API call**

POST https://app.pipedrive.com/signup/start

**Request Headers**

> > Host: app.pipedrive.com  
> > User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0  
> > Accept: application/json  
> > Accept-Language: en-US,en;q=0.5  
> > Accept-Encoding: gzip, deflate, br  
> > Referer: https://www.pipedrive.com/en/log-out-successful  
> > Content-Type: application/json  
> > Content-Length: 167  
> > Origin: https://www.pipedrive.com  
> > Alt-Used: app.pipedrive.com  
> > Connection: keep-alive  
> > Sec-Fetch-Dest: empty  
> > Sec-Fetch-Mode: cors  
> > Sec-Fetch-Site: same-site  
> > Pragma: no-cache  
> > Cache-Control: no-cache  
> > TE: trailers

**Request object for user signup**

`{"email":"**email**","language":"en","country_code":"nl","selectedTier":null,"packages":[],"optimizelyEndUserId":null,"consentGiven":true,"marketingConsent":true}`

**Response object if user exist:**

`{"emailInUse":true}`

**Response object if user doesnt exist:**

`{"redirectUrl":"https://app.pipedrive.com/signup"}`
