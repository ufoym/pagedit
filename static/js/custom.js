if (!RedactorPlugins) var RedactorPlugins = {};

RedactorPlugins.save = {
    init: function ()
    {
        this.buttonAdd('save', 'Save', this.saveButton);
        this.buttonAwesome('save', 'fa-save');
    },
    saveButton: function(buttonName, buttonDOM, buttonObj, e)
    {
        $.ajax({
            url: '/_/contents/save',
            type: 'post',
            data: 'content=' + $('#content').redactor('get')
        });
    }
};