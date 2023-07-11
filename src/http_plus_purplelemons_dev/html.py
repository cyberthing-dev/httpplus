
"""
HTML objects can be Void or Base.

Base HTML objects have children and are wrapped in a tag <abc> like this </abc>.
Void HTML objects do not have children and are not wrapped in a tag <efg />.
"""

class Style:
    def __init__(self, **styles:str) -> None:
        self.styles = styles
    def __str__(self) -> str:
        return ';'.join([f'{key}:{value}' for key, value in self.styles.items()])+";" if self.styles else ''

class VoidHTMLObject:
    def __str__(self) -> str: return self.as_string()

    @staticmethod
    def boolify(string:"bool|str") -> str:
        if isinstance(string, bool):
            return "true" if string is True else "false" if string is False else None
        return string if string in {"true", "false"} else None

    def __init__(self,
        /,
        accesskey:str=None,
        class_:str=None,
        contenteditable:"str|bool"=None,
        dir:str=None,
        draggable:"str|bool"=None,
        hidden:"str|bool"=None,
        id:"str|int"=None,
        lang:str=None,
        spellcheck:"str|bool"=None,
        style:"str|Style"=None,
        tabindex:str=None,
        title:str=None,
        translate:str=None
    ):
        """
        Read about global attributes here: https://www.w3schools.com/tags/ref_standardattributes.asp

        Args:
            accesskey (str): Specifies a keybind/shortcut to focus an element.
            class_ (str): Specifies one or more classnames for an element.
            contenteditable (str): Whether the content of an element is editable or not. Can be "true" or "false".
            dir (str): The directionality of text. Can be "ltr", "rtl", or "auto".
            draggable (str): Whether an element is draggable or not. Can be "true" or "false".
            hidden (str): Specifies that an element is not yet, or is no longer, relevant. Can be "true" or "false".
            id (str): Specifies a unique id for an element.
            lang (str): Specifies the language of the element's content.
            spellcheck (str): Whether the element is to have its spelling and grammar checked or not. Can be "true" or "false".
            style (str): Specifies an inline CSS style for an element.
            tabindex (str): Specifies the order that elements are focused when the user navigates through a document with the tab key.
            title (str): Specifies extra information about an element.
            translate (str): Specifies whether the content of an element should be translated or not. Can be "yes" or "no".
            children (list[BaseHTMLObject]): A list of child elements. Can be added later with the `add_child` method.
        """
        self.tag = self.__class__.__name__.lower()
        self.accesskey = accesskey
        self.class_ = class_
        self.contenteditable = self.boolify(contenteditable)
        self.dir = dir
        self.draggable = self.boolify(draggable)
        self.hidden = self.boolify(hidden)
        self.id = f"{id}"
        self.lang = lang
        self.spellcheck = self.boolify(spellcheck)
        self.style = f"{style}"
        self.tabindex = tabindex
        self.title = title
        self.translate = translate

    def as_string(self) -> str:
        attrs = ' '.join(f'{key}="{value}"' for key, value in self.__dict__.items() if value is not None and key != 'tag')
        return f"<{self.tag} {attrs} />"

class BaseHTMLObject(VoidHTMLObject):
    def __init__(self, /, children:list["VoidHTMLObject|str"]=None, **kwargs):
        super().__init__(**kwargs)
        self.children = children or []

    def as_string(self) -> str:
        attrs = ' '.join(f'{key}="{value}"' for key, value in self.__dict__.items() if value is not None and key != 'tag' and key != 'children')
        children = '\n'.join(str(child) for child in self.children)
        return f"<{self.tag} {attrs}>{children}</{self.tag}>"

class Input(VoidHTMLObject):
    """
    Input element. Used like this:

    ```html
    <input type="text" name="name" placeholder="Enter your name" />
    ```

    Read more here: https://www.w3schools.com/tags/tag_input.asp
    """

    def __init__(self,
        /,
        accept:str=None,
        alt:str=None,
        autocomplete:str=None,
        autofocus:"str|bool"=None,
        checked=None,
        dirname:str=None,
        disabled:str=None,
        form:str=None,
        formaction:str=None,
        formenctype:str=None,
        formmethod:str=None,
        formnovalidate:str=None,
        formtarget:str=None,
        height:"int|str"=None,
        list:str=None,
        max:str=None,
        maxlength:str=None,
        min:str=None,
        minlength:str=None,
        multiple:str=None,
        name:str=None,
        pattern:str=None,
        placeholder:str=None,
        readonly:str=None,
        required:str=None,
        size:str=None,
        src:str=None,
        step:str=None,
        type_:str=None,
        value:str=None,
        width:"int|str"=None,
        **kwargs
    ):
        """
        In addition to the arguments for `BaseHTMLObject`, this class also has the following arguments:

        Args:
            accept (str): Specifies the types of files that the server accepts (only for type="file").
            alt (str): Specifies an alternate text for images when the cursor hovers over it (only for type="image").
            autocomplete (str): Specifies whether a form should have autocomplete "on" or "off".
            autofocus (str): Specifies that an input field should automatically get focus when the page loads. Can be "true" or "false".
            checked (any): Set to any value other than `None`. Specifies that an input element should be pre-selected when the page loads (for type="checkbox" or type="radio").
            dirname (str): Specifies that the value of the input field should be submitted by a form under the name of the dirname attribute.
            disabled (any): Set to any value other than `None`. Specifies that an input field should be disabled.
            form (str): Set to the id of the form you want this input to be associated with.
            formaction (str): Specifies where to send the form-data when a form is submitted. Only for type="submit" and type="image".
            formenctype (str): Specifies how form-data should be encoded before sending it to a server. Only for type="submit" and type="image".
            formmethod (str): Specifies how to send the form-data ("get" or "post"). Only for type="submit" and type="image".
            formnovalidate (any): Set to any value other than `None`. Specifies that the form-data should not be validated on submission. Only for type="submit" and type="image".
            formtarget (str): Specifies where to display the response after submitting the form. Only for type="submit" and type="image".
            height (int|str): Specifies the height of an input field in pixels (only for type="image").
            list (str): Use the id of a `<datalist>` element which defines list of options.
            max (str): Specifies the maximum value for an input field, e.g. number, date, etc. (only for type="number" or type="range").
            maxlength (str): Specifies the maximum number of characters allowed in an input field (only for type="text" or type="password").
            min (str): Specifies the minimum value for an input field, e.g. number, date, etc. (only for type="number" or type="range").
            minlength (str): Specifies the minimum number of characters allowed in an input field (only for type="text" or type="password").
            multiple (any): Set to any value other than `None`. Specifies that a user can enter more than one value in an input field (only for type="email" or type="file").
            name (str): Name this field!
            pattern (str): Should be a regular expression that an input field's value is checked against (only for type="text", type="search", type="url", type="tel", or type="email").
            placeholder (str): Specifies a short hint that describes the expected value of an input field (e.g. a sample value or a short description of the expected format).
            readonly (any): Set to any value other than `None`. Specifies that this input field cannot be overwritten.
            required (any): Set to any value other than `None`. Specifies that an input field must be filled out before submitting the form.
            size (str): Specifies the width of an input field, in characters (only for type="text", type="password", type="search", type="tel", type="url", or type="email").
            src (str): Specifies the URL of the image to use as a submit button (only for type="image").
            step (str): Specifies the legal number intervals for an input field (only for type="number" or type="range").
            type_ (str): Specifies the type of `<input>` element to display.
            value (str): Specifies some predefined value for the input field. You should use `placeholder` if you want to give an example.
            width (int|str): Specifies the width of an input field in pixels (only for type="image").
        """
        super().__init__(**kwargs)
        self.accept = accept
        self.alt = alt
        self.autocomplete = "on" if autocomplete=="on" else "off" if autocomplete=="off" else None
        self.autofocus = self.boolify(autofocus)
        self.checked = checked
        self.dirname = dirname
        self.disabled = disabled
        self.form = form
        self.formaction = formaction
        self.formenctype = "application/x-www-form-urlencoded" if formenctype=="application/x-www-form-urlencoded" else "multipart/form-data" if formenctype=="multipart/form-data" else "text/plain" if formenctype=="text/plain" else None
        self.formmethod = "get" if formmethod=="get" else "post" if formmethod=="post" else None
        self.formnovalidate = formnovalidate
        self.formtarget = formtarget
        self.height = str(height)
        self.list = list
        self.max = max
        self.maxlength = maxlength
        self.min = min
        self.minlength = minlength
        self.multiple = multiple
        self.name = name
        self.pattern = pattern
        self.placeholder = placeholder
        self.readonly = readonly
        self.required = required
        self.size = size
        self.src = src
        self.step = step
        self.type = type_
        self.value = value
        self.width = str(width)
# now some people may ask why i did use beautifulsoup for this
# thats a great question

class Form(BaseHTMLObject):
    """
    Form element. Used like this:

    ```html
    <form action="/action_page.php">
        Name:<br>
        <input type="text" name="name" placeholder="My name is...">
    </form>
    ```

    Read more here: https://www.w3schools.com/tags/tag_input.asp
    """

    def __init__(self,
        /,
        accept_charset:str=None,
        action:str=None,
        autocomplete:str=None,
        enctype:str=None,
        method:str=None,
        name:str=None,
        novalidate:str=None,
        target:str=None,
        **kwargs
    ):
        """
        In addition to the arguments for `BaseHTMLObject`, this class also has the following arguments:
        Args:
            accept_charset (str): Specifies the character encodings that are to be used for the form submission.
            action (str): Specifies where to send the form-data when a form is submitted.
            autocomplete (str): Specifies whether a form should have autocomplete on or off.
            enctype (str): Specifies how the form-data should be encoded when submitting it to the server.
            method (str): Specifies the HTTP method to use when sending form-data.
            name (str): Specifies the name of a form.
            novalidate (str): Specifies that the form-data should not be validated on submission.
            target (str): Specifies where to display the response after submitting the form.
        """
        self.accept_charset = accept_charset
        self.action = action
        self.autocomplete = "on" if autocomplete=="on" else "off" if autocomplete=="off" else None
        self.enctype = "application/x-www-form-urlencoded" if enctype=="application/x-www-form-urlencoded" else "multipart/form-data" if enctype=="multipart/form-data" else "text/plain" if enctype=="text/plain" else None
        self.method = "get" if method=="get" else "post" if method=="post" else None
        self.name = name
        self.novalidate = novalidate
        self.target = target
        super().__init__(**kwargs)

class Area(BaseHTMLObject):
    """
    Area element. Used like this:

    ```html
    <img src="map.png" usemap="#image-map">
    <map name="image-map">
        <area target="" alt="Computer" title="Computer" href="com.html" coords="34,44,270,350" shape="rect">
    </map>
    ```

    Read more here: https://www.w3schools.com/tags/tag_area.asp
    """

    def __init__(self,
        /,
        alt:str=None,
        coords:str=None,
        download:str=None,
        href:str=None,
        hreflang:str=None,
        media:str=None,
        reffererpolicy:str=None,
        rel:str=None,
        shape:str=None,
        target:str=None,
        type_:str=None,
        **kwargs
    ):
        """
        In addition to the arguments for `BaseHTMLObject`, this class also has the following arguments:
        Args:
            alt (str): Specifies an alternate text for the area, if the image is not available.
            coords (str): Can be `x1,y1,x2,y2`, or `x,y,radius`, or a long list of `x,y` coordinates for a polygon. See the `shape` parameter.
            download (str): Specify the filename of the file to be downloaded when a user clicks on the hyperlink.
            href (str): Specifies the URL of the page the link goes to.
            hreflang (str): Specifies the language of the linked document.
            media (str): Specifies what media/device the target resource is optimized for.
            reffererpolicy (str): Specifies which referrer to send when fetching the resource.
            rel (str): Specifies the relationship between the current document and the linked document.
            shape (str): Can be `default`, `rect`, `circle`, or `poly`.
            target (str): Specifies where to open the linked document.
            type_ (str): Specifies the media type of the linked document.
        """
        self.alt = alt
        self.coords = coords
        self.download = download
        self.href = href
        self.hreflang = hreflang
        self.media = media
        self.reffererpolicy = reffererpolicy
        self.rel = rel
        self.shape = "default" if shape=="default" else "rect" if shape=="rect" else "circle" if shape=="circle" else "poly" if shape=="poly" else None
        self.target = target
        self.type = type_
        super().__init__(**kwargs)

class Img(VoidHTMLObject):
    def __init__(self,
        /,
        alt:str=None,
        crossorigin:str=None,
        height:str=None,
        ismap:str=None,
        loading:str=None,
        referrerpolicy:str=None,
        sizes:str=None,
        src:str=None,
        srcset:str=None,
        usemap:str=None,
        width:str=None,
        **kwargs
    ):
        """
        In addition to the arguments for `BaseHTMLObject`, this class also has the following arguments:

        Args:
            alt (str): Specifies an alternate text for an image, if the image cannot be displayed.
            crossorigin (str): Specifies how the element handles crossorigin requests. Can be `anonymous` or `use-credentials`.
            height (str): Specifies the height of the image.
            ismap (any): Set to any value other than None to use this image as a server-side image-map.
            loading (str): Specifies whether an image should be loaded immediately ("eager"), or when it is near to the viewport ("lazy").
            referrerpolicy (str): Specifies which referrer to send when fetching the image. Can be `no-referrer`, `no-referrer-when-downgrade`, `origin`, `origin-when-cross-origin`, `strict-origin-when-cross-origin`, or `unsafe-url`.
            sizes (str): Specifies the size of the image.
            src (str): Specifies the URL of the image.
            srcset (str): Specifies the URL of the image to use in different situations.
            usemap (str): Use the format of `#mapname` where `mapname` is in some map element `<map name="mapname"> ... </map>`.
            width (str): Width of the image.
        """
        self.alt = alt
        self.crossorigin = "anonymous" if crossorigin=="anonymous" else "use-credentials" if crossorigin=="use-credentials" else None
        self.height = height
        self.ismap = ismap
        self.loading = "eager" if loading=="eager" else "lazy" if loading=="lazy" else None
        self.referrerpolicy = "no-referrer" if referrerpolicy=="no-referrer" else "no-referrer-when-downgrade" if referrerpolicy=="no-referrer-when-downgrade" else "origin" if referrerpolicy=="origin" else "origin-when-cross-origin" if referrerpolicy=="origin-when-cross-origin" else "unsafe-url" if referrerpolicy=="unsafe-url" else None
        self.sizes = sizes
        self.src = src
        self.srcset = srcset
        self.usemap = usemap
        self.width = width
        super().__init__(**kwargs)

class Script(BaseHTMLObject):
    def __init__(self,
        /,
        async_:str=None,
        crossorigin:str=None,
        defer:str=None,
        integrity:str=None,
        nomodule:"bool|str"=None,
        referrerpolicy:str=None,
        src:str=None,
        type_:str=None,
        **kwargs
    ):
        """
        In addition to the arguments for `BaseHTMLObject`, this class also has the following arguments:

        Args:
            async_ (str): Set to any value other than None to load the script asynchronously.
            crossorigin (str): Specifies how the element handles crossorigin requests. Can be `anonymous` or `use-credentials`.
            defer (any): Set to any value other than None to load the script when the page has finished parsing.
            integrity (str): Use a hash of the `src` file.
            nomodule (bool|str): Set to any value other than None to prevent the script from running if the browser supports ES6 modules.
            referrerpolicy (str): Specifies which referrer to send when fetching the script. Can be `no-referrer`, `no-referrer-when-downgrade`, `origin`, `origin-when-cross-origin`, `strict-origin-when-cross-origin`, or `unsafe-url`.
            src (str): Specifies the URL of an external script.
            type_ (str): Specifies the media type of the script.
        """
        self.async_ = async_
        self.crossorigin = "anonymous" if crossorigin=="anonymous" else "use-credentials" if crossorigin=="use-credentials" else None
        self.defer = defer
        self.integrity = integrity
        self.nomodule = self.boolify(nomodule)
        self.referrerpolicy = "no-referrer" if referrerpolicy=="no-referrer" else "no-referrer-when-downgrade" if referrerpolicy=="no-referrer-when-downgrade" else "origin" if referrerpolicy=="origin" else "origin-when-cross-origin" if referrerpolicy=="origin-when-cross-origin" else "same-origin" if referrerpolicy=="same-origin" else "strict-origin" if referrerpolicy=="strict-origin" else "strict-origin-when-cross-origin" if referrerpolicy=="strict-origin-when-cross-origin" else "unsafe-url" if referrerpolicy=="unsafe-url" else None
        self.src = src
        self.type = type_
        super().__init__(**kwargs)

class Button(BaseHTMLObject):
    def __init__(self,
        /,
        autofocus:str=None,
        disabled:str=None,
        form:str=None,
        formaction:str=None,
        formenctype:str=None,
        formmethod:str=None,
        formnovalidate:str=None,
        formtarget:str=None,
        name:str=None,
        type_:str=None,
        value:str=None,
        **kwargs
    ):
        """
        In addition to the arguments for `BaseHTMLObject`, this class also has the following arguments:

        Args:
            autofocus (any): Set to any value other than None to automatically focus the button when the page loads.
            disabled (any): Set to any value other than None to disable the button.
            form (str): Specifies one or more forms the button belongs to.
            formaction (str): Specifies where to send the form-data when a form is submitted.
            formenctype (str): Specifies how form-data should be encoded before sending it to a server. Can be `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain`.
            formmethod (str): Specifies how to send the form-data (which HTTP method to use).
            formnovalidate (any): Set to any value other than None to disable form validation. Only for `type="submit"`.
            formtarget (str): Specifies where to display the response after submitting the form.
            name (str): Specifies a name for the button.
            type_ (str): Specifies the type of button. Can be `submit`, `reset`, or `button`.
            value (str): Specifies an initial value for the button.
        """
        self.autofocus = autofocus
        self.disabled = disabled
        self.form = form
        self.formaction = formaction
        self.formenctype = "application/x-www-form-urlencoded" if formenctype=="application/x-www-form-urlencoded" else "multipart/form-data" if formenctype=="multipart/form-data" else "text/plain" if formenctype=="text/plain" else None
        self.formmethod = "get" if formmethod=="get" else "post" if formmethod=="post" else None
        self.formnovalidate = formnovalidate
        self.formtarget = formtarget
        self.name = name
        type_=type_.lower()
        self.type = "submit" if type_=="submit" else "reset" if type_=="reset" else "button" if type_=="button" else None
        self.value = value
        super().__init__(**kwargs)
