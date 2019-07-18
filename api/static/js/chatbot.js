var chat = {
    messageToSend: '',
    
    init: function() {
      this.cacheDOM();
      this.bindEvents();
      this.render();
    },
    cacheDOM: function() {
      this.$chatHistory = $('.chat-history');
      this.$button = $('button');
      this.$textarea = $('#message-to-send');
      this.$chatHistoryList =  this.$chatHistory.find('ul');
    },
    bindEvents: function() {
      this.$button.on('click', this.addMessage.bind(this));
      this.$textarea.on('keyup', this.addMessageEnter.bind(this));
    },
    getBotMessage(userMessage, context, onComplete) {
    
        $.ajax({
          url: "/api/chatbot/message",
          type: "POST",
          data: {
              user_message: userMessage
          },
          success: function(data, textStatus, xhr) {
            console.log(data)
              if (data.error === 0) {
                  onComplete(data.bot_message, context)
              }
              else console.log(data.msg);
          }
      }); 
    },
    render: function() {
      this.scrollToBottom();
      if (this.messageToSend.trim() !== '') {
          var template = Handlebars.compile( $("#message-template").html());
          var context = { 
              messageOutput: this.messageToSend,
              time: this.getCurrentTime()
          };
          
          this.$chatHistoryList.append(template(context));
          this.scrollToBottom();
          this.$textarea.val('');
          
          // responses
          this.getBotMessage(this.messageToSend.trim(), this, function (botMessage, context) {
              var templateResponse = Handlebars.compile( $("#message-response-template").html());
              console.log(botMessage)
              var contextResponse = { 
                  response: botMessage,
                  time: context.getCurrentTime()
              };
              context.$chatHistoryList.append(templateResponse(contextResponse));
              context.scrollToBottom();
          });
      }
    },
    addMessage: function() {
      this.messageToSend = this.$textarea.val()
      this.render();         
    },
    addMessageEnter: function(event) {
        // enter was pressed
        if (event.keyCode === 13) {
          this.addMessage();
        }
    },
    scrollToBottom: function() {
       this.$chatHistory.scrollTop(this.$chatHistory[0].scrollHeight);
    },
    getCurrentTime: function() {
      return new Date().toLocaleTimeString().
              replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3");
    }
  };

(function(){   
    chat.init();
// Minimize chat button

    $(".chat-header").on("click", function(){
        if($(".minimize-button").html() == "-"){
            $(".minimize-button").html("+");
            $(".chat-history").addClass("hidden")
            $(".chat-message").addClass("hidden")
            $(".chat-container").attr("style", "height: 60px")
        }
        else{
            $(".minimize-button").html("-");
            $(".chat-history").removeClass("hidden")
            $(".chat-message").removeClass("hidden")
            $(".chat-container").attr("style", "height: 363px")
        }
    });


// Speech to text recognition
    try {
        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        var recognition = new SpeechRecognition();

        recognition.onresult = function(event) {
            // event is a SpeechRecognitionEvent object.
            // It holds all the lines we have captured so far. 
            // We only need the current one.
            var current = event.resultIndex;
            
            // Get a transcript of what was said.
            var transcript = event.results[current][0].transcript;
            
            // Add the current transcript to the contents of our Note.
            $("#message-to-send").val(transcript)
            chat.addMessage();
            // recognition.stop();
            $('.microphone').removeClass("listening")
            $('.microphone').removeAttr("style")
            $("#message-to-send").attr("placeholder", "Digite uma mensagem...")
        }
    }
    catch(e) {
        console.error(e);
        $('.no-browser-support').show();
        $('.app').hide();
    }

    $('.microphone').on('click', function(e) {
        if ($('.microphone').hasClass("listening")) {
            $('.microphone').removeClass("listening")
            $('.microphone').removeAttr("style")
            $("#message-to-send").attr("placeholder", "Digite uma mensagem...")
            recognition.stop();
        }
        else {
            $('.microphone').addClass("listening")
            $('.microphone').attr("style", "color: #86bb71;")
            recognition.start();
            $("#message-to-send").val("")
            $("#message-to-send").attr("placeholder", "Escutando...")
        }        
      });

  })();
  
